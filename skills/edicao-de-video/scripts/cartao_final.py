"""Cartão final com a cara do produto, desenhado sobre o último quadro do vídeo.

Uso: python cartao_final.py fundo.jpg saida.png [largura altura] [cartao.json]

Layout (escala a partir de 720 px de largura):
- fundo: o próprio último quadro, desfocado, com um véu da cor da marca e degradê escuro embaixo;
- topo: nome da marca e uma linha de apoio;
- meio: cartão branco arredondado com selo, título e 2 a 3 linhas de texto, mais um rodapé pequeno;
- embaixo: botão na cor da marca com a chamada e uma seta apontando para o botão real do anúncio.

cartao.json (todos os campos são opcionais):
{
  "marca": "Minha Marca", "apoio": "Uma linha sobre o produto",
  "selo": "1'", "titulo": "Haz el test gratis",
  "linhas": ["En 1 minuto descubre qué", "necesita tu cuerpo"],
  "rodape": "en casa · a tu ritmo",
  "botao": "Toca en más información",
  "cor": [232, 67, 126], "cor_escura": [176, 38, 92], "tinta": [40, 28, 40]
}
Texto longo demais no botão: diminua o texto, não a fonte (a fonte já é reduzida para caber).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIN = "C:/Windows/Fonts/"
FONTES = {"forte": [WIN + "seguibl.ttf", WIN + "arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
          "media": [WIN + "seguisb.ttf", WIN + "arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
          "leve": [WIN + "segoeui.ttf", WIN + "arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]}
PADRAO = {"marca": "", "apoio": "", "selo": "", "titulo": "", "linhas": [], "rodape": "",
          "botao": "Toca en más información", "cor": [232, 67, 126], "cor_escura": [176, 38, 92],
          "tinta": [40, 28, 40]}


def font(peso, tam):
    for f in FONTES[peso]:
        if Path(f).exists():
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def centro(d, y, texto, f, cor, W, sombra=None):
    x = (W - d.textlength(texto, font=f)) / 2
    if sombra:
        d.text((x + 3, y + 3), texto, font=f, fill=sombra)
    d.text((x, y), texto, font=f, fill=cor)


def cabe(d, texto, peso, tam, largura):
    f = font(peso, tam)
    while d.textlength(texto, font=f) > largura and tam > 10:
        tam -= 1
        f = font(peso, tam)
    return f


def main():
    fundo, saida = sys.argv[1], sys.argv[2]
    W, H = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (720, 1280)
    cfg = dict(PADRAO)
    if len(sys.argv) > 5:
        cfg.update(json.loads(Path(sys.argv[5]).read_text(encoding="utf-8")))
    cor, escura, tinta = tuple(cfg["cor"]), tuple(cfg["cor_escura"]), tuple(cfg["tinta"])
    k = W / 720

    bg = Image.open(fundo).convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(14 * k))
    bg = Image.blend(bg, Image.new("RGB", (W, H), cor), 0.45)
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(150 * max(0, (y - H * 0.55) / (H * 0.45))))
    bg = Image.composite(Image.new("RGB", (W, H), escura), bg, grad.resize((W, H)))
    d = ImageDraw.Draw(bg)

    if cfg["marca"]:
        centro(d, int(150 * k), cfg["marca"], cabe(d, cfg["marca"], "forte", int(64 * k), W - 80 * k), "white", W,
               sombra=tuple(max(0, c - 110) for c in escura))
    if cfg["apoio"]:
        centro(d, int(240 * k), cfg["apoio"], cabe(d, cfg["apoio"], "media", int(34 * k), W - 80 * k), "white", W)

    if cfg["titulo"] or cfg["linhas"]:
        cx0, cy0, cx1, cy1 = int(60 * k), int(430 * k), W - int(60 * k), int(760 * k)
        sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle((cx0 + 6 * k, cy0 + 10 * k, cx1 + 6 * k, cy1 + 10 * k),
                                                 radius=int(36 * k), fill=(0, 0, 0, 70))
        sb = sombra.filter(ImageFilter.GaussianBlur(10 * k))
        bg.paste(sb, (0, 0), sb)
        d = ImageDraw.Draw(bg)
        d.rounded_rectangle((cx0, cy0, cx1, cy1), radius=int(36 * k), fill="white")
        if cfg["selo"]:
            sx, sy, sr = W // 2, cy0, int(46 * k)
            d.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=cor, outline="white", width=int(5 * k))
            centro(d, sy - int(30 * k), cfg["selo"], font("forte", int(46 * k)), "white", W)
        larg = cx1 - cx0 - 50 * k
        if cfg["titulo"]:
            centro(d, cy0 + int(70 * k), cfg["titulo"], cabe(d, cfg["titulo"], "forte", int(58 * k), larg), cor, W)
        for i, ln in enumerate(cfg["linhas"][:3]):
            centro(d, cy0 + int((160 + 45 * i) * k), ln, cabe(d, ln, "media", int(32 * k), larg), tinta, W)
        if cfg["rodape"]:
            centro(d, cy0 + int(262 * k), cfg["rodape"], cabe(d, cfg["rodape"], "leve", int(26 * k), larg),
                   (120, 105, 120), W)

    if cfg["botao"]:
        bx0, by0, bx1, by1 = int(90 * k), int(870 * k), W - int(90 * k), int(980 * k)
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=int(55 * k), fill=cor, outline="white", width=int(4 * k))
        fb = cabe(d, cfg["botao"], "forte", int(40 * k), bx1 - bx0 - 50 * k)
        centro(d, by0 + (by1 - by0 - fb.size * 1.25) / 2, cfg["botao"], fb, "white", W)
        ax, ay = W // 2, int(1040 * k)
        d.polygon([(ax - 34 * k, ay), (ax + 34 * k, ay), (ax, ay + 44 * k)], fill="white")
    bg.save(saida)
    print("ok", saida, W, H)


if __name__ == "__main__":
    main()
