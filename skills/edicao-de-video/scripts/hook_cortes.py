"""Monta o hook por cortes: cada trecho (inicio, fim, velocidade) vira um segmento 24 fps 720x1280;
o ultimo termina com fade para branco (flash). Acao importante fica em 1,0x; so deslocamento acelera.

Uso:
  python hook_cortes.py bruto.mp4 saida.mp4 "0.30-1.50@1.2" "3.00-3.80@1.0" "5.50-7.70@1.0"
Opcional: --ganho-primeiro 12 --ganho-resto 14 --flash 0.25
"""
import argparse, os, subprocess, tempfile


def seg(src, a, b, db, out, flash=0.0, sp=1.0):
    d = (b - a) / sp
    vf = f'setpts=(PTS-STARTPTS)/{sp},fps=24,format=yuv420p,scale=720:1280'
    if flash:
        vf += f",fade=t=out:st={d - flash:.3f}:d={flash}:color=white"
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(a), '-to', str(b), '-i', src, '-filter_complex',
                    f'[0:v]{vf}[v];[0:a]asetpts=PTS-STARTPTS,atempo={sp},aresample=48000,apad,volume={db}dB[a]',
                    '-map', '[v]', '-map', '[a]', '-shortest', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast',
                    '-c:a', 'pcm_s16le', out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bruto'); ap.add_argument('saida'); ap.add_argument('cortes', nargs='+')
    ap.add_argument('--ganho-primeiro', type=float, default=12); ap.add_argument('--ganho-resto', type=float, default=14)
    ap.add_argument('--flash', type=float, default=0.25)
    a = ap.parse_args()
    cortes = []
    for c in a.cortes:
        t, _, sp = c.partition('@')
        ini, fim = (float(x) for x in t.split('-'))
        cortes.append((ini, fim, float(sp or 1.0)))
    with tempfile.TemporaryDirectory() as w:
        for i, (ini, fim, sp) in enumerate(cortes):
            seg(a.bruto, ini, fim, a.ganho_primeiro if i == 0 else a.ganho_resto, os.path.join(w, f'h{i}.mov'),
                flash=a.flash if i == len(cortes) - 1 else 0.0, sp=sp)
        lista = os.path.join(w, 'l.txt')
        open(lista, 'w').write(''.join(f"file 'h{i}.mov'\n" for i in range(len(cortes))))
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista,
                        '-af', 'alimiter=limit=0.7:level=false', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
                        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', a.saida], check=True)
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.saida],
                       capture_output=True, text=True).stdout.strip()
    print(a.saida, d, 's')


if __name__ == '__main__':
    main()
