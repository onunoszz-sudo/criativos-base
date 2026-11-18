"""Monta um pre-hook curto sem fala (ex.: o "pre-hook do carro" da Appyon), por receita JSON.

Uso: python prehook.py receita.json [saida.mp4]

O que importa num pre-hook (aprendido com a referência do Pedro, 2026-11-18):
- O SOM SEGURA A RETENÇÃO. Cada ação visível tem o seu som, no quadro exato: tampa do pote abrindo,
  tapete levantando, tapete caindo, mão alisando o tapete, porta batendo. Vídeo de IA quase sempre vem
  sem esses sons (ou baixos demais): eles entram como "foley", recortados de outro take ou de outro
  vídeo, e presos ao instante da ação pelo tempo da cena de origem ("cena" + "ponto").
- Os níveis seguem a referência, camada por camada (bloco "niveis"): riser, música, foley e snap.
  Não se normaliza o vídeo inteiro para -14 LUFS, porque isso muda o equilíbrio entre as camadas.
- O snap cai no corte para o último plano; o flash branco vem depois, subindo devagar, e é a ponte
  para o avatar falando. A headline some no branco.

Receita (caminhos relativos à pasta da receita):
{
  "cenas": [   # em ordem. velocidade > 1 só onde não há som importante; "som_db": null deixa a cena muda
    {"arquivo": "take1.mp4", "inicio": 0.15, "fim": 0.75, "velocidade": 1.5, "som_db": null}
  ],
  "foley": [   # cada som preso a um ponto da cena (tempo no arquivo da cena) ou a "em" (s no vídeo final)
    {"nome": "tampa", "arquivo": "take3.mp4", "inicio": 0.62, "fim": 1.15, "ancora": 0.70,
     "cena": 1, "ponto": 0.84, "db": 0},      # "ancora" (tempo no arquivo do som) cai em "ponto" da "cena"
    {"nome": "areia", "sintetico": "areia", "segundos": 1.6, "cena": 2, "ponto": 1.75, "db": -10}
  ],
  "niveis": {  # alvos medidos na referência (RMS de (L+R)/2, dBFS); veja "Níveis" no SKILL.md
    "riser_rms_inicio": -40.7,  # riser sozinho, antes do primeiro som
    "musica_rms": -35.5,        # música sozinha
    "foley_pico": -19.2,        # pico (janela de 0,1 s) do som de ação mais forte; o "db" do foley é relativo a ele
    "snap_pico": -11.6          # pico do snap
  },
  "riser": {"arquivo": "riser.wav", "segundos": 1.9, "janela": 0.45},   # janela: onde o alvo do riser foi medido
  "musica": {"arquivo": "interstellar.mp3", "inicio": 23, "fator": 0.95, "fade_in": 0.35, "entra": 1.9},
  "snap": {"arquivo": "snap.wav", "ataque": 0.04},   # "ataque": onde está o estalo dentro do arquivo
  "flash": {"comeca": 0.22, "pico": 0.44, "segura": 0.06, "desce": 0.17, "alpha": 0.92},  # s depois do corte final
  "final_apos_corte": 1.2,     # quanto do último plano entra (headline, flash e começo do corpo)
  "headline": ["IT WORKS SO FAST", "IT IS SCARY!"], "bandeiras": true,
  "resolucao": [1080, 1920], "saida": "pre-hook.mp4"
}
"""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SR = 48000
LIMPA = "highpass=f=120,afftdn=nf=-45"   # tira o ronco grave e o chiado de fundo do take de IA


def run(*a):
    subprocess.run([str(x) for x in a], check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode().strip())


def ler(p, a=None, b=None, fator=1.0, filtro=None):
    """Áudio estéreo float32 a 48 kHz. fator != 1 muda velocidade e tom juntos (o 0,95x com tom alterado)."""
    cmd = ["ffmpeg", "-v", "error"]
    if a is not None:
        cmd += ["-ss", f"{a:.3f}"]
    if b is not None:
        cmd += ["-t", f"{b - (a or 0):.3f}"]
    af = [f"aresample={SR}"]
    if fator != 1:
        af += [f"asetrate={SR * fator:.0f}", f"aresample={SR}"]
    if filtro:
        af.append(filtro)
    cmd += ["-i", str(p), "-af", ",".join(af), "-ac", "2", "-f", "f32le", "-"]
    return np.frombuffer(subprocess.check_output(cmd), np.float32).reshape(-1, 2).copy()


def rms_db(x):
    m = x.mean(axis=1) if x.ndim == 2 else x
    return 20 * np.log10(np.sqrt(np.mean(m.astype(np.float64) ** 2)) + 1e-9)


def pico_db(x, w=0.1):
    m = (x.mean(axis=1) if x.ndim == 2 else x).astype(np.float64)
    n = int(w * SR)
    if len(m) <= n:
        return rms_db(m)
    c = np.cumsum(np.concatenate([[0], m ** 2]))
    e = (c[n:] - c[:-n]) / n
    return 10 * np.log10(e[::int(0.01 * SR)].max() + 1e-12)


def fade(x, d_in=0.005, d_out=0.03):
    x = x.copy()
    a, b = int(d_in * SR), int(d_out * SR)
    if a and len(x) > a:
        x[:a] *= np.linspace(0, 1, a)[:, None]
    if b and len(x) > b:
        x[-b:] *= np.linspace(1, 0, b)[:, None]
    return x


def areia(seg, seed=3):
    """Canela/areia caindo: grãos curtos de ruído, filtrados entre 1,5 e 7 kHz, com envelope."""
    rng = np.random.default_rng(seed)
    n = int(seg * SR)
    sig = np.zeros(n)
    for t in rng.integers(0, n - 200, int(seg * 2600)):
        L = int(rng.integers(40, 160))
        sig[t:t + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.2, 1)
    F = np.fft.rfft(sig)
    f = np.fft.rfftfreq(n, 1 / SR)
    F *= ((f > 1500) & (f < 7000)) * 1.0 + ((f >= 300) & (f <= 1500)) * 0.25
    sig = np.fft.irfft(F, n)
    t = np.linspace(0, 1, n)
    env = np.minimum(1, t / 0.12) * np.minimum(1, (1 - t) / 0.25) * (0.8 + 0.2 * np.sin(2 * np.pi * 3.1 * t * seg))
    sig *= env
    sig /= np.abs(sig).max() + 1e-9
    return np.stack([sig, sig * 0.96], axis=1).astype(np.float32)


def bandeira(w):
    h = int(w * 0.63)
    im = Image.new("RGBA", (w, h), "white")
    d = ImageDraw.Draw(im)
    for i in range(13):
        if i % 2 == 0:
            d.rectangle((0, i * h / 13, w, (i + 1) * h / 13), fill=(178, 34, 52))
    cw, chh = w * 0.42, h * 7 / 13
    d.rectangle((0, 0, cw, chh), fill=(60, 59, 110))
    for r in range(5):
        for c in range(6):
            x, y = cw * (c + 0.5) / 6, chh * (r + 0.5) / 5
            d.ellipse((x - w * 0.012, y - w * 0.012, x + w * 0.012, y + w * 0.012), fill="white")
    return im


def bandeiras_cruzadas(largura_total):
    """Duas bandeirinhas com mastro, cruzadas em X (como o sticker da referência)."""
    fw = int(largura_total * 0.46)
    plen = int(fw * 1.45)
    can = Image.new("RGBA", (fw + 16, plen + 10), (0, 0, 0, 0))
    g = ImageDraw.Draw(can)
    px = fw + 8
    g.line([(px, 8), (px, plen + 8)], fill=(170, 170, 176), width=max(3, fw // 18))
    g.ellipse([px - fw // 16, 0, px + fw // 16, fw // 8], fill=(205, 45, 45))
    can.alpha_composite(bandeira(fw).transpose(Image.FLIP_LEFT_RIGHT), (px - 2 - fw, 9))
    esq = can.rotate(24, resample=Image.BICUBIC, expand=True)
    dir_ = esq.transpose(Image.FLIP_LEFT_RIGHT)
    sob = int(esq.width * 0.30)
    out = Image.new("RGBA", (esq.width * 2 - sob, esq.height), (0, 0, 0, 0))
    out.alpha_composite(esq, (0, 0))
    out.alpha_composite(dir_, (esq.width - sob, 0))
    return out


def sobreposicao(linhas, bandeiras, W, H, out):
    """Headline medida na referência: linha mais longa com ~68% da largura, topo a ~10% da altura."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fonte_arq = next((f for f in ["C:/Windows/Fonts/arialbd.ttf",
                                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if Path(f).exists()), None)
    maior = max(linhas, key=len) if linhas else ""
    tam = int(W * 0.08)
    if fonte_arq and maior:
        while tam > 10 and d.textlength(maior, font=ImageFont.truetype(fonte_arq, tam)) > W * 0.685:
            tam -= 1
    fonte = ImageFont.truetype(fonte_arq, tam) if fonte_arq else ImageFont.load_default()
    y = int(H * 0.098)
    for ln in linhas:
        x = (W - d.textlength(ln, font=fonte)) / 2
        d.text((x + 3, y + 4), ln, font=fonte, fill=(0, 0, 0, 120))
        d.text((x, y), ln, font=fonte, fill="white", stroke_width=max(3, tam // 13), stroke_fill="black")
        y += int(tam * 1.02)
    if bandeiras:
        b = bandeiras_cruzadas(int(W * 0.17))
        im.alpha_composite(b, ((W - b.width) // 2, y - int(tam * 0.05)))
    im.save(out)


def main():
    rp = Path(sys.argv[1]).resolve()
    base = rp.parent
    R = json.loads(rp.read_text(encoding="utf-8"))
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else base / R.get("saida", "pre-hook.mp4")
    W, H = R.get("resolucao", [1080, 1920])
    N = {"riser_rms_inicio": -40.7, "musica_rms": -35.5, "foley_pico": -19.2, "snap_pico": -11.6}
    N.update(R.get("niveis", {}))
    tmp = Path(tempfile.mkdtemp(prefix="prehook_"))

    # 1. linha do tempo das cenas
    cenas, t = [], 0.0
    for c in R["cenas"]:
        v = c.get("velocidade", 1.0)
        cenas.append({**c, "t0": t, "dur": (c["fim"] - c["inicio"]) / v})
        t += (c["fim"] - c["inicio"]) / v
    ult = cenas[-1]
    corte = ult["t0"]
    v = ult.get("velocidade", 1.0)
    ult["fim"] = min(ult["fim"], ult["inicio"] + R.get("final_apos_corte", 1.2) * v)
    ult["dur"] = (ult["fim"] - ult["inicio"]) / v
    T = corte + ult["dur"]

    def no_video(cena, ponto):
        c = cenas[cena]
        return c["t0"] + (ponto - c["inicio"]) / c.get("velocidade", 1.0)

    # 2. imagem: cortes e velocidades, sem zoom
    vparts = []
    for i, c in enumerate(cenas):
        vf = (f"trim={c['inicio']}:{c['fim']},setpts=(PTS-STARTPTS)/{c.get('velocidade', 1.0)},fps=30,"
              f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1")
        n = tmp / f"v{i:02d}.mp4"
        run("ffmpeg", "-v", "error", "-y", "-i", base / c["arquivo"], "-vf", vf, "-an", "-c:v", "libx264",
            "-preset", "medium", "-crf", "16", n)
        vparts.append(n)
    lst = tmp / "lista.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in vparts), encoding="utf-8")
    junto = tmp / "junto.mp4"
    run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", junto)

    # 3. som, camada por camada, no nível da referência
    n_total = int(T * SR) + SR
    mix = np.zeros((n_total, 2), np.float32)
    rel = []

    def soma(x, em, nome, ganho_db):
        x = x * (10 ** (ganho_db / 20))
        i = int(round(em * SR))
        if i < 0:
            x, i = x[-i:], 0
        j = min(n_total, i + len(x))
        mix[i:j] += x[:j - i]
        rel.append(f"{nome:14s} em {em:5.2f}s  ganho {ganho_db:+6.1f} dB  pico {pico_db(x):6.1f}  rms {rms_db(x):6.1f}")

    for i, c in enumerate(cenas):                      # som próprio das cenas (opcional)
        if c.get("som_db") is None:
            continue
        x = ler(base / c["arquivo"], c["inicio"], c["fim"], filtro=LIMPA)
        vv = c.get("velocidade", 1.0)
        if vv != 1.0:
            idx = np.arange(0, len(x), vv).astype(int)
            x = x[idx[idx < len(x)]]
        soma(fade(x, 0.01, 0.02), c["t0"], f"cena{i}", c["som_db"])

    rz = R.get("riser")
    if rz:
        x = ler(base / rz["arquivo"])[: int(rz.get("segundos", 1.9) * SR)]
        janela = x[: int(rz.get("janela", 0.45) * SR)]   # a mesma janela em que o alvo foi medido na referência
        soma(fade(x, 0.0, 0.06), 0.0, "riser", N["riser_rms_inicio"] - rms_db(janela))

    M = R.get("musica")
    if M:
        f = M.get("fator", 0.95)
        entra = M.get("entra", rz.get("segundos", 1.9) if rz else 0.0)
        ini = M.get("inicio", 0)
        x = ler(base / M["arquivo"], ini, ini + (T - entra) * f + 0.5, fator=f)[: int((T - entra) * SR)]
        fi = M.get("fade_in", 0.35)
        x = fade(x, fi, 0.05)
        soma(x, entra, "musica", N["musica_rms"] - rms_db(x[int(fi * SR):]))

    for k, fo in enumerate(R.get("foley", [])):
        if fo.get("sintetico") == "areia":
            x, anc = areia(fo.get("segundos", 1.5), seed=k + 3), 0.0
        else:
            x = ler(base / fo["arquivo"], fo["inicio"], fo["fim"], filtro=fo.get("filtro", LIMPA))
            anc = fo.get("ancora", fo["inicio"]) - fo["inicio"]
        x = fade(x, fo.get("fade_in", 0.004), fo.get("fade_out", 0.03))
        em = (no_video(fo["cena"], fo["ponto"]) if "cena" in fo else fo["em"]) - anc
        soma(x, em, fo.get("nome", f"foley{k}"), N["foley_pico"] + fo.get("db", 0) - pico_db(x))

    S = R.get("snap")
    if S:
        x = ler(base / S["arquivo"])
        soma(fade(x, 0.0, 0.05), corte - S.get("ataque", 0.04), "snap", N["snap_pico"] - pico_db(x))

    mix = mix[: int(T * SR)]
    lim = 10 ** (-1 / 20)
    if np.abs(mix).max() > lim:   # só segura os picos acima de -1 dBFS
        g = np.minimum(1.0, lim / (np.abs(mix).max(axis=1) + 1e-9))
        g = np.convolve(g, np.ones(240) / 240, mode="same")
        mix = mix * np.minimum(1.0, g)[:, None]
        mix = np.clip(mix, -lim, lim)
    wav = tmp / "som.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())

    # 4. headline até o flash + flash branco depois do snap
    png = tmp / "topo.png"
    sobreposicao(R.get("headline", []), R.get("bandeiras", True), W, H, png)
    F = {"comeca": 0.22, "pico": 0.44, "segura": 0.06, "desce": 0.17, "alpha": 0.92}
    F.update(R.get("flash", {}))
    f0, f1 = corte + F["comeca"], corte + F["pico"]
    f2 = f1 + F["segura"]
    some = f1 + F["segura"] / 2
    vfx = (f"[0:v][2:v]overlay=0:0:enable='lt(t,{some:.3f})'[v1];"
           f"color=c=white:s={W}x{H}:r=30:d={T:.3f},format=rgba,colorchannelmixer=aa={F['alpha']},"
           f"fade=t=in:st={f0:.3f}:d={f1 - f0:.3f}:alpha=1,fade=t=out:st={f2:.3f}:d={F['desce']:.3f}:alpha=1[fl];"
           f"[v1][fl]overlay=0:0:shortest=1,format=yuv420p[vout]")
    run("ffmpeg", "-v", "error", "-y", "-i", junto, "-i", wav, "-loop", "1", "-i", png, "-filter_complex", vfx,
        "-map", "[vout]", "-map", "1:a", "-t", f"{T:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-c:a", "aac", "-ar", str(SR), "-b:a", "256k", "-movflags", "+faststart", out)
    print("\n".join(rel))
    print(f"corte final {corte:.2f}s | flash {f0:.2f}-{f2 + F['desce']:.2f}s | headline some {some:.2f}s")
    print("ok", out.name, round(dur(out), 2), "s")


if __name__ == "__main__":
    main()
