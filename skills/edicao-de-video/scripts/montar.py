"""Monta um vídeo vertical a partir de cenas curtas (geradas por IA ou gravadas), por receita JSON.

Uso: python montar.py receita.json [saida.mp4]

O que faz, na ordem:
1. corta o silêncio do começo e do fim de cada cena (usa as palavras do whisper; fica `pre` s antes da
   primeira palavra e `pos` s depois da última). Cena sem fala fica com os primeiros `sem_fala_secs`;
2. zoom lento alternado (aproxima / afasta) para a imagem não ficar parada;
3. cartão final (opcional): `produto` (cartao_final.py sobre o último quadro), `cor` (fundo liso com linhas
   de texto) ou nenhum;
4. trilha por bloco de cenas, com fade na troca e ducking (a música abaixa quando alguém fala);
5. legenda palavra por palavra (opcional);
6. faixa fixa no topo (opcional, ex.: "BLACK NOVEMBER");
7. velocidade (ex.: 1.15) e áudio final a -14 LUFS.

Campos da receita (caminhos relativos à pasta da receita). Só `cenas` é obrigatório:
{
  "cenas": "clips",                  # pasta com as cenas, em ordem alfabética
  "padrao": "cena*.mp4",
  "falas": "falas.json",             # {"cena01": "texto exato da fala", ...}; cena fora daqui = sem fala
  "idioma": "es",                    # idioma do whisper
  "pre": 0.12, "pos": 0.30, "sem_fala_secs": 4.0,
  "zoom": true,
  "resolucao": [720, 1280],
  "musica": {"pasta": "musica", "db": -16, "blocos": {"tensao": ["cena01"], "final": ["cena02", "fim"]}},
                                     # cada bloco usa <pasta>/<nome-do-bloco>.mp3
  "legenda": {"fonte": "Arial Black", "tamanho": 64, "margem_baixo": 330, "maiusculas": true},
  "cartao": {"tipo": "produto", "config": "cartao.json", "segundos": 2.2},
         ou {"tipo": "cor", "cor": "0x13804f", "linhas": [["Toca en", 64, "white"], ["más información", 64, "white"]]},
  "faixa": {"texto": "BLACK NOVEMBER", "cor_fundo": "0x000000", "cor_texto": "0xFFD84D", "y": 18, "altura": 90},
  "velocidade": 1.15,
  "saida": "video.mp4"
}

Erros que este script já evita (não remova):
- `fps=30` ANTES do zoompan: com d=1 ele gera 1 quadro por quadro de entrada; cena de 24 fps sem isso fica
  acelerada e a boca sai de sincronia;
- no drawbox a altura do vídeo é `ih`, não `h` (h é a altura da caixa).
Precisa de: ffmpeg/ffprobe no PATH e `pip install faster-whisper` (só se houver falas ou legenda).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

FONTS = "C\\:/Windows/Fonts/" if sys.platform.startswith("win") else "/usr/share/fonts/truetype/dejavu/"
FONTE_TEXTO = "ariblk.ttf" if sys.platform.startswith("win") else "DejaVuSans-Bold.ttf"


def run(*a, cwd=None):
    subprocess.run([str(x) for x in a], check=True, cwd=cwd)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode().strip())


def ass_time(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")


def main():
    receita_path = Path(sys.argv[1]).resolve()
    base = receita_path.parent
    R = json.loads(receita_path.read_text(encoding="utf-8"))
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else base / R.get("saida", "video.mp4")
    cdir = base / R["cenas"]
    clips = sorted(cdir.glob(R.get("padrao", "cena*.mp4")))
    if not clips:
        sys.exit(f"nenhuma cena em {cdir}")
    W, H = R.get("resolucao", [720, 1280])
    falas = {}
    if R.get("falas"):
        falas = json.loads((base / R["falas"]).read_text(encoding="utf-8"))
    pre, pos, sem_fala = R.get("pre", 0.12), R.get("pos", 0.30), R.get("sem_fala_secs", 4.0)
    tmp = Path(tempfile.mkdtemp(prefix="montar_"))
    model = None
    if falas or R.get("legenda"):
        from faster_whisper import WhisperModel
        model = WhisperModel("small", device="cpu", compute_type="int8")

    parts, events, marks, t0 = [], [], [], 0.0
    for k, c in enumerate(clips):
        full = dur(c)
        words = []
        if model is not None and c.stem in falas:
            segs, _ = model.transcribe(str(c), language=R.get("idioma", "pt"), word_timestamps=True)
            words = [w for s in segs for w in (s.words or [])]
        texto = falas.get(c.stem)
        if texto is None or not words:
            a, b, timed = 0.0, min(sem_fala, full) if falas else full, []
        else:
            a = max(0.0, words[0].start - pre)
            b = min(full, words[-1].end + pos)
            alvo = texto.split()
            if len(alvo) == len(words):
                timed = [(w.start, w.end, x) for w, x in zip(words, alvo)]
            else:  # contagem diferente: distribui o texto certo no intervalo falado
                ini, fim = words[0].start, words[-1].end
                step = (fim - ini) / len(alvo)
                timed = [(ini + i * step, ini + (i + 1) * step, x) for i, x in enumerate(alvo)]
        d = b - a
        n = tmp / f"p{k:02d}.mp4"
        frames = max(1, int(round(d * 30)))
        if R.get("zoom", True):
            z = f"1+0.07*on/{frames}" if k % 2 == 0 else f"1.07-0.07*on/{frames}"
            vf = (f"fps=30,scale={W * 2}:{H * 2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d=1:s={W}x{H}:fps=30,setsar=1")
        else:
            vf = f"fps=30,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
        cena(c, a, d, vf, n)
        dn = dur(n)
        for s, e, w in timed:
            s2, e2 = s - a, e - a
            if 0 <= s2 < dn:
                events.append((t0 + s2, t0 + min(e2, s2 + 1.2, dn), w))
        marks.append((c.stem, t0, t0 + dn))
        parts.append(n); t0 += dn
        print(c.stem, f"{full:.2f}s -> {dn:.2f}s")

    # cartão final
    C = R.get("cartao")
    if C:
        secs = C.get("segundos", 2.2)
        end = tmp / "fim.mp4"
        if C["tipo"] == "produto":
            fundo, png = tmp / "fundo.jpg", tmp / "cartao.png"
            run("ffmpeg", "-v", "error", "-y", "-sseof", "-0.2", "-i", parts[-1], "-frames:v", "1", fundo)
            args = [sys.executable, str(Path(__file__).parent / "cartao_final.py"), fundo, png, str(W), str(H)]
            if C.get("config"):
                args.append(str(base / C["config"]))
            run(*args)
            fr = int(secs * 30)
            run("ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", png, "-f", "lavfi", "-i",
                "anullsrc=r=48000:cl=stereo", "-t", str(secs), "-vf",
                f"scale={W * 2}:{H * 2},zoompan=z='1+0.04*on/{fr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d=1:s={W}x{H}:fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-c:a", "aac", "-ar", "48000", "-ac", "2", end)
        else:
            linhas = C.get("linhas", [])
            y0 = H / 2 - 45 * len(linhas)
            dt = []
            for i, (txt, tam, cor) in enumerate(linhas):
                dt.append(f"drawtext=fontfile='{FONTS}{FONTE_TEXTO}':text='{esc(txt)}':fontcolor={cor}:"
                          f"fontsize={tam}:x=(w-text_w)/2:y={y0 + i * 95:.0f}")
            run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                f"color=c={C.get('cor', 'black')}:s={W}x{H}:d={secs}:r=30", "-f", "lavfi", "-i",
                "anullsrc=r=48000:cl=stereo", "-t", str(secs), "-vf", ",".join(dt) or "null",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2", end)
        marks.append(("fim", t0, t0 + secs)); parts.append(end); t0 += secs
    total = t0

    lst = tmp / "lista.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    cur = tmp / "junto.mp4"
    run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cur)

    # trilha por bloco + ducking
    M = R.get("musica")
    if M:
        mus = base / M.get("pasta", "musica")
        blocos = M["blocos"]
        ini = {b: min(t for s, t, _ in marks if s in cenas) for b, cenas in blocos.items()}
        fim = {b: max(t for s, _, t in marks if s in cenas) for b, cenas in blocos.items()}
        nomes = list(blocos)
        fx, inputs, labels = [], [], []
        for i, b in enumerate(nomes):
            s, e = ini[b], fim[b]
            L = e - s + (0.6 if i < len(nomes) - 1 else 0)
            inputs += ["-i", str(mus / f"{b}.mp3")]
            fx.append(f"[{i + 1}:a]atrim=0:{L:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.6,"
                      f"afade=t=out:st={max(0, L - 0.8):.3f}:d=0.8,volume={M.get('db', -16)}dB,"
                      f"adelay={int(s * 1000)}|{int(s * 1000)},apad=whole_dur={total:.3f}[m{i}]")
            labels.append(f"[m{i}]")
        fx.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,atrim=0:{total:.3f}[mus]")
        fx.append("[0:a]asplit=2[voz][sc]")
        fx.append("[mus][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck]")
        fx.append("[voz][duck]amix=inputs=2:normalize=0[mix]")
        nxt = tmp / "mix.mp4"
        run("ffmpeg", "-v", "error", "-y", "-i", cur, *inputs, "-filter_complex", ";".join(fx),
            "-map", "0:v", "-map", "[mix]", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "192k", nxt)
        cur = nxt

    # legenda palavra por palavra + faixa
    vfs = []
    L = R.get("legenda")
    if L and events:
        head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: %d\nPlayResY: %d\n\n[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
                "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
                "MarginL, MarginR, MarginV, Encoding\n"
                "Style: W,%s,%d,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,40,40,%d,1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n") % (
            W, H, L.get("fonte", "Arial Black"), L.get("tamanho", 64), L.get("margem_baixo", 330))
        lines = []
        for i, (s, e, w) in enumerate(events):
            nx = events[i + 1][0] if i + 1 < len(events) else e
            e = min(max(e, s + 0.18), nx) if nx > s else e
            lines.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},W,,0,0,0,,{w.upper() if L.get('maiusculas', True) else w}")
        (tmp / "legenda.ass").write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
        vfs.append("ass=legenda.ass")
    F = R.get("faixa")
    if F:
        y, hh = F.get("y", 18), F.get("altura", 90)
        vfs.append(f"drawbox=x=0:y={y}:w=iw:h={hh}:color={F.get('cor_fundo', '0x000000')}@1:t=fill,"
                   f"drawtext=fontfile='{FONTS}{FONTE_TEXTO}':text='{esc(F['texto'])}':fontcolor="
                   f"{F.get('cor_texto', '0xFFD84D')}:fontsize={int(hh * 0.62)}:x=(w-text_w)/2:y={y}+({hh}-text_h)/2")
    if vfs:
        nxt = tmp / "capt.mp4"
        run("ffmpeg", "-v", "error", "-y", "-i", cur.name, "-vf", ",".join(vfs), "-c:v", "libx264", "-preset", "slow",
            "-crf", "18", "-c:a", "copy", nxt.name, cwd=tmp)
        cur = nxt

    vel = float(R.get("velocidade", 1.0))
    if vel != 1.0:
        run("ffmpeg", "-v", "error", "-y", "-i", cur, "-vf", f"setpts=PTS/{vel},fps=30", "-c:v", "libx264",
            "-preset", "slow", "-crf", "18", "-af", f"atempo={vel},loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac",
            "-ar", "48000", "-b:a", "192k", "-movflags", "+faststart", out)
    else:
        run("ffmpeg", "-v", "error", "-y", "-i", cur, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-c:a", "aac", "-ar", "48000", "-b:a", "192k", "-movflags", "+faststart", out)
    print("ok", out.name, round(dur(out), 2), "s,", len(events), "palavras")


def has_audio(p):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                 "stream=index", "-of", "csv=p=0", str(p)]).decode().strip()
    return bool(o)


def cena(c, a, d, vf, n):
    """Corta e reenquadra uma cena. Cena sem áudio ganha silêncio, para o concat não quebrar."""
    if has_audio(c):
        run("ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", c, "-vf", vf,
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2",
            "-b:a", "192k", n)
    else:
        run("ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", c, "-f", "lavfi", "-i",
            "anullsrc=r=48000:cl=stereo", "-vf", vf, "-map", "0:v", "-map", "1:a", "-shortest",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2",
            "-b:a", "192k", n)


if __name__ == "__main__":
    main()
