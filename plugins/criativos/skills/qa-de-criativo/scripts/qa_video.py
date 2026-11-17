"""QA técnico de um vídeo de anúncio antes de subir. Só lê: não altera o arquivo.

Uso: python qa_video.py video.mp4 [--roteiro roteiro.txt] [--idioma es] [--max 90] [--min 5]

Checagens (PASSA / ATENÇÃO / NÃO PASSA):
- formato: 9:16, pelo menos 720 px de largura;
- duração dentro de --min e --max (segundos);
- primeiro quadro não é preto (o Reels usa o primeiro quadro em vários lugares);
- quadros pretos no meio (blackdetect, 0,3 s ou mais);
- áudio quebrado no começo: mais de 1 pacote de áudio com duração < 0,01 s nos primeiros 3 s
  (defeito visto em ganchos colados pelo Grok) ou silêncio digital (< -60 dB) de 1,2 s+ nos primeiros
  5 s (pausa natural de fala fica abaixo disso);
- volume integrado perto de -14 LUFS (aceita de -17 a -11);
- pronúncia: com --roteiro, transcreve com o whisper e lista as palavras do roteiro que não aparecem
  na fala (ex.: "equipos" saiu "enquimos"). Números do roteiro são comparados por extenso e por algarismo.
Precisa de ffmpeg/ffprobe e, para a pronúncia, `pip install faster-whisper`.
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from difflib import SequenceMatcher


def sh(*a):
    return subprocess.run([str(x) for x in a], capture_output=True, text=True, encoding="utf-8", errors="replace")


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--roteiro")
    ap.add_argument("--idioma", default="pt")
    ap.add_argument("--max", type=float, default=180)
    ap.add_argument("--min", type=float, default=3)
    a = ap.parse_args()
    v = a.video
    res = []

    info = json.loads(sh("ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                         "-of", "json", v).stdout)
    vs = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    W, H, D = vs["width"], vs["height"], float(info["format"]["duration"])
    tem_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    ok916 = abs(W / H - 9 / 16) < 0.01 and W >= 720
    res.append(("formato", "PASSA" if ok916 else "NÃO PASSA", f"{W}x{H}"))
    res.append(("duração", "PASSA" if a.min <= D <= a.max else "NÃO PASSA", f"{D:.1f} s (limite {a.min:g} a {a.max:g})"))

    y = sh("ffmpeg", "-hide_banner", "-i", v, "-frames:v", "1", "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
           "-f", "null", "-").stderr
    m = re.search(r"YAVG=([\d.]+)", y)
    yavg = float(m.group(1)) if m else -1
    res.append(("primeiro quadro", "NÃO PASSA" if 0 <= yavg < 20 else "PASSA", f"brilho médio {yavg:.0f} (preto < 20)"))

    bd = sh("ffmpeg", "-hide_banner", "-i", v, "-vf", "blackdetect=d=0.3:pix_th=0.10", "-an", "-f", "null", "-").stderr
    pretos = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bd)
    meio = [(float(s), float(e)) for s, e in pretos if float(s) > 0.05 and float(e) < D - 0.05]
    res.append(("quadros pretos no meio", "ATENÇÃO" if meio else "PASSA",
                ", ".join(f"{s:.1f}-{e:.1f} s" for s, e in meio) or "nenhum"))

    if tem_audio:
        pk = sh("ffprobe", "-v", "error", "-select_streams", "a", "-read_intervals", "%+3", "-show_entries",
                "packet=pts_time,duration_time", "-of", "csv=p=0", v).stdout.split()
        mini = 0
        for ln in pk:
            p = ln.split(",")
            try:
                if len(p) > 1 and float(p[1]) < 0.01:
                    mini += 1
            except ValueError:
                pass
        sd = sh("ffmpeg", "-hide_banner", "-t", "5", "-i", v, "-af", "silencedetect=noise=-60dB:d=1.2", "-vn",
                "-f", "null", "-").stderr
        sil = re.findall(r"silence_start: ([\d.]+)", sd)
        quebrado = mini > 1 or bool(sil)
        det = []
        if mini > 1:
            det.append(f"{mini} pacotes < 0,01 s")
        if sil:
            det.append("silêncio digital no gancho em " + ", ".join(f"{float(x):.1f} s" for x in sil))
        res.append(("áudio do gancho", "NÃO PASSA" if quebrado else "PASSA", "; ".join(det) or "ok"))
        lu = sh("ffmpeg", "-hide_banner", "-i", v, "-af", "ebur128", "-vn", "-f", "null", "-").stderr
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lu)
        lufs = float(m[-1]) if m else 0
        res.append(("volume", "PASSA" if -17 <= lufs <= -11 else "ATENÇÃO", f"{lufs:.1f} LUFS (alvo -14)"))
    else:
        res.append(("áudio", "ATENÇÃO", "o vídeo não tem trilha de áudio"))

    if a.roteiro:
        from faster_whisper import WhisperModel
        texto = open(a.roteiro, encoding="utf-8").read()
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segs, _ = model.transcribe(v, language=a.idioma)
        falado = " ".join(s.text for s in segs)
        r = [norm(w) for w in texto.split() if norm(w)]
        f = [norm(w) for w in falado.split() if norm(w)]
        sm = SequenceMatcher(None, r, f, autojunk=False)
        faltam = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "replace" and any(x.isdigit() for x in f[j1:j2]) and (j2 - j1) <= (i2 - i1):
                continue  # número dito por extenso no roteiro e transcrito em algarismo: não é erro
            if op in ("replace", "delete"):
                faltam.append(" ".join(r[i1:i2]) + (f" -> ouvido: {' '.join(f[j1:j2])}" if op == "replace" else " -> não dito"))
        nota = sm.ratio()
        st = "PASSA" if not faltam else ("ATENÇÃO" if nota >= 0.9 else "NÃO PASSA")
        res.append(("pronúncia x roteiro", st, f"semelhança {nota:.0%}" + ("; " + " | ".join(faltam[:8]) if faltam else "")))
        print("TRANSCRIÇÃO:", falado.strip(), file=sys.stderr)

    print(f"QA de {v}")
    for nome, st, det in res:
        print(f"- {nome}: {st} ({det})")
    final = "NÃO PASSA" if any(s == "NÃO PASSA" for _, s, _ in res) else (
        "PASSA COM ATENÇÃO" if any(s == "ATENÇÃO" for _, s, _ in res) else "PASSA")
    print("RESULTADO:", final)
    sys.exit(1 if final == "NÃO PASSA" else 0)


if __name__ == "__main__":
    main()
