"""Confere os takes de fala baixados do Flow: descobre o avatar/cena pelo primeiro quadro (o take comeca
na imagem base), transcreve com o Whisper medium e compara palavra por palavra com a copy.

Uso:
  python -I conferir_takes.py <pasta_mp4> --falas falas.json --refs <pasta_imagens_base>
falas.json: {"t01": "texto...", "t02": "..."}; refs: uma imagem por avatar/cena (nome do arquivo = rotulo).
Saida: conf.json na pasta, com rotulo, take, razao, diferencas e fim da ultima palavra.
Take sem fala = hook (o Whisper as vezes inventa texto no ASMR: conferir na folha de quadros).
"""
import argparse, difflib, json, re, subprocess
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel


def norm(s):
    s = s.lower().replace('-', ' ').replace('gonna', 'going to')
    return re.sub(r"[^a-z0-9 ]", " ", s).split()


def thumb(path, ss=None):
    cmd = ['ffmpeg', '-v', 'error'] + (['-ss', str(ss)] if ss is not None else []) + \
          ['-i', str(path), '-frames:v', '1', '-vf', 'scale=36:64', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.uint8).astype(float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pasta'); ap.add_argument('--falas', required=True); ap.add_argument('--refs', required=True)
    a = ap.parse_args()
    falas = json.load(open(a.falas, encoding='utf-8'))
    refs = {p.stem: thumb(p) for p in Path(a.refs).iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.png')}
    m = WhisperModel('medium.en', device='cpu', compute_type='int8')
    out = []
    for f in sorted(Path(a.pasta).glob('*.mp4')):
        t0 = thumb(f, 0.05)
        rot = min(refs, key=lambda k: np.mean((refs[k] - t0) ** 2)); dist = round(float(np.mean((refs[rot] - t0) ** 2)), 1)
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'],
                             capture_output=True).stdout
        audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        segs, _ = m.transcribe(audio, language='en', word_timestamps=True, condition_on_previous_text=False,
                               initial_prompt='Transcribe every word verbatim, including repeated words.')
        ws = [w for s in segs for w in s.words]; txt = ' '.join(w.word.strip() for w in ws)
        if not ws:
            out.append(dict(arq=f.name, ref=rot, dist=dist, id='hook')); print(f.name, rot, 'HOOK'); continue
        tid = max(falas, key=lambda k: difflib.SequenceMatcher(None, norm(txt), norm(falas[k])).ratio())
        sm = difflib.SequenceMatcher(None, norm(falas[tid]), norm(txt))
        dif = [f"{op}:{' '.join(norm(falas[tid])[i1:i2])}->{' '.join(norm(txt)[j1:j2])}"
               for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal']
        out.append(dict(arq=f.name, ref=rot, dist=dist, id=tid, razao=round(sm.ratio(), 2), dif=dif, texto=txt,
                        fim=round(ws[-1].end, 2), ultima=round(ws[-1].end - ws[-1].start, 2)))
        alerta = ' ULTIMA PALAVRA LONGA' if ws[-1].end - ws[-1].start > 0.6 else ''
        print(f.name, rot, dist, tid, round(sm.ratio(), 2), dif, alerta, flush=True)
    json.dump(out, open(Path(a.pasta) / 'conf.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
