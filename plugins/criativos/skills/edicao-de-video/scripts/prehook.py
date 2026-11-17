"""Monta um pre-hook curto sem fala (ex.: o "pre-hook do carro" da Appyon), por receita JSON.

Uso: python prehook.py receita.json [saida.mp4]

Receita (caminhos relativos à pasta da receita):
{
  "cenas": [                                      # em ordem; cada trecho pode ser acelerado
    {"arquivo": "abre-pote.mp4", "inicio": 0.4, "fim": 2.6, "velocidade": 1.0, "realce_db": 4},
    {"arquivo": "entra-carro.mp4", "inicio": 0.0, "fim": 3.0, "velocidade": 1.4}
  ],
  "headline": ["IT WORKS SO FAST", "IT IS SCARY!"],   # branco com contorno preto, no topo
  "bandeiras": true,                              # duas bandeirinhas dos EUA logo abaixo da headline
  "musica": {"arquivo": "musica.mp3", "inicio": 23, "fator": 0.95, "db": -8, "fade_in": 0.35},
                                                  # fator muda velocidade E tom juntos (asetrate)
  "riser": {"arquivo": null, "db": -12, "segundos": 1.9},   # null = gera um riser sintético
  "snap": {"arquivo": null, "db": -4, "flash": true},       # estalo no fim, com flash branco
  "sons": [{"arquivo": "porta.mp3", "em": 4.8, "db": -6}],  # efeitos extras em segundos do vídeo final
  "resolucao": [1080, 1920],
  "saida": "pre-hook.mp4"
}

Regras da receita (call da Appyon de 2026-11-17):
- começa no primeiro movimento e o primeiro quadro nunca é preto;
- trechos sem som importante vão acelerados;
- a música entra no fim do riser, com fade-in curto, baixa, a 0,95x com o tom alterado (para não tomar
  bloqueio de direito autoral);
- o snap fica nos últimos 0,4 s, com o flash sincronizado.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def run(*a):
    subprocess.run([str(x) for x in a], check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode().strip())


def has_audio(p):
    return bool(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                         "stream=index", "-of", "csv=p=0", str(p)]).decode().strip())


def bandeira(w):
    """Bandeira dos EUA simples (13 listras e cantão azul), desenhada em vez de emoji."""
    h = int(w * 0.62)
    im = Image.new("RGBA", (w, h), "white")
    d = ImageDraw.Draw(im)
    for i in range(13):
        if i % 2 == 0:
            d.rectangle((0, i * h / 13, w, (i + 1) * h / 13), fill=(178, 34, 52))
    d.rectangle((0, 0, w * 0.4, h * 7 / 13), fill=(60, 59, 110))
    for r in range(4):
        for c in range(5):
            x, y = w * 0.04 + c * w * 0.075, h * 0.06 + r * h * 0.12
            d.ellipse((x, y, x + w * 0.025, y + w * 0.025), fill="white")
    return im


def sobreposicao(linhas, bandeiras, W, H, out):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tam = int(W * 0.062)
    fonte = None
    for f in ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if Path(f).exists():
            fonte = ImageFont.truetype(f, tam)
            break
    fonte = fonte or ImageFont.load_default()
    y = int(H * 0.095)
    for ln in linhas:
        x = (W - d.textlength(ln, font=fonte)) / 2
        d.text((x, y), ln, font=fonte, fill="white", stroke_width=max(3, tam // 12), stroke_fill="black")
        y += int(tam * 1.08)
    if bandeiras:
        b = bandeira(int(W * 0.06))
        g = int(W * 0.008)
        x0 = (W - 2 * b.width - g) // 2
        for i, ang in enumerate((8, -8)):
            r = b.rotate(ang, expand=True)
            im.alpha_composite(r, (x0 + i * (b.width + g), y + int(tam * 0.15)))
    im.save(out)


def main():
    rp = Path(sys.argv[1]).resolve()
    base = rp.parent
    R = json.loads(rp.read_text(encoding="utf-8"))
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else base / R.get("saida", "pre-hook.mp4")
    W, H = R.get("resolucao", [1080, 1920])
    tmp = Path(tempfile.mkdtemp(prefix="prehook_"))

    # 1. trechos (com velocidade e realce do som)
    parts = []
    for i, c in enumerate(R["cenas"]):
        src = base / c["arquivo"]
        a, b = c.get("inicio", 0.0), c.get("fim", dur(src))
        v = c.get("velocidade", 1.0)
        vf = (f"trim={a}:{b},setpts=(PTS-STARTPTS)/{v},fps=30,scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},setsar=1")
        n = tmp / f"t{i:02d}.mp4"
        if has_audio(src):
            at = []
            vv = v
            while vv > 2.0:  # atempo aceita no máximo 2.0 por filtro
                at.append("atempo=2.0"); vv /= 2.0
            at.append(f"atempo={vv:.4f}")
            af = f"atrim={a}:{b},asetpts=PTS-STARTPTS,{','.join(at)},volume={c.get('realce_db', 0)}dB"
            run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "medium",
                "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2", n)
        else:
            run("ffmpeg", "-v", "error", "-y", "-i", src, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-vf", vf, "-map", "0:v", "-map", "1:a", "-shortest", "-c:v", "libx264", "-preset", "medium",
                "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2", n)
        parts.append(n)
    lst = tmp / "lista.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    junto = tmp / "junto.mp4"
    run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", junto)
    T = dur(junto)

    # 2. sons: riser, música, snap, extras
    inputs, fx, mix = ["-i", str(junto)], ["[0:a]anull[base]"], ["[base]"]
    k = 1
    rz = R.get("riser", {"db": -12, "segundos": 1.9})
    rs = rz.get("segundos", 1.9) if rz is not None else 0.0
    if rz is not None:
        if rz.get("arquivo"):
            inputs += ["-i", str(base / rz["arquivo"])]
            fx.append(f"[{k}:a]atrim=0:{rs},asetpts=PTS-STARTPTS,volume={rz.get('db', -12)}dB[rz]")
        else:
            inputs += ["-f", "lavfi", "-t", str(rs), "-i",
                       f"aevalsrc='0.12*sin(2*PI*(180+520*t/{rs})*t)+0.06*(random(0)*2-1)*t/{rs}':s=48000"]
            fx.append(f"[{k}:a]afade=t=in:d={rs * 0.8:.2f},highpass=f=120,pan=stereo|c0=c0|c1=c0,"
                      f"volume={rz.get('db', -12)}dB[rz]")
        mix.append("[rz]"); k += 1
    M = R.get("musica")
    if M:
        f = M.get("fator", 0.95)
        inputs += ["-ss", str(M.get("inicio", 0)), "-i", str(base / M["arquivo"])]
        st = int(rs * 1000)
        fx.append(f"[{k}:a]aresample=48000,asetrate={48000 * f:.0f},aresample=48000,afade=t=in:d={M.get('fade_in', 0.35)},"
                  f"volume={M.get('db', -8)}dB,adelay={st}|{st},atrim=0:{T:.3f}[mu]")
        mix.append("[mu]"); k += 1
    S = R.get("snap", {"db": -4, "flash": True})
    snap_t = max(0.0, T - 0.4)
    if S is not None:
        if S.get("arquivo"):
            inputs += ["-i", str(base / S["arquivo"])]
        else:
            inputs += ["-f", "lavfi", "-t", "0.09", "-i", "anoisesrc=d=0.09:c=white:a=0.9:r=48000"]
        ms = int(snap_t * 1000)
        fx.append(f"[{k}:a]highpass=f=1800,afade=t=out:st=0.005:d=0.08,pan=stereo|c0=c0|c1=c0,volume={S.get('db', -4)}dB,"
                  f"adelay={ms}|{ms}[sn]")
        mix.append("[sn]"); k += 1
    for j, s in enumerate(R.get("sons", [])):
        inputs += ["-i", str(base / s["arquivo"])]
        ms = int(s["em"] * 1000)
        fx.append(f"[{k}:a]volume={s.get('db', -6)}dB,adelay={ms}|{ms}[x{j}]")
        mix.append(f"[x{j}]"); k += 1
    fx.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0,atrim=0:{T:.3f},"
              "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

    # 3. imagem: headline + bandeiras + flash do snap
    png = tmp / "topo.png"
    sobreposicao(R.get("headline", []), R.get("bandeiras", True), W, H, png)
    inputs += ["-loop", "1", "-i", str(png)]
    vfx = [f"[0:v][{k}:v]overlay=0:0:shortest=1[v1]"]
    if S is not None and S.get("flash", True):
        vfx.append(f"color=c=white:s={W}x{H}:r=30:d={T:.3f},format=rgba,"
                   f"fade=t=in:st={snap_t:.3f}:d=0.05:alpha=1,fade=t=out:st={snap_t + 0.05:.3f}:d=0.15:alpha=1[fl]")
        vfx.append("[v1][fl]overlay=0:0:shortest=1[vout]")
    else:
        vfx.append("[v1]null[vout]")
    run("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fx + vfx), "-map", "[vout]",
        "-map", "[aout]", "-t", f"{T:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-b:a", "192k", "-movflags", "+faststart", out)
    print("ok", out.name, round(dur(out), 2), "s")


if __name__ == "__main__":
    main()
