"""Estado de cada vídeo (e do lote do dia) num arquivo pequeno, para não depender da conversa.

Cada vídeo tem uma pasta com `estado.json`. Este script lê e muda só o pedaço necessário, então dá
para limpar o chat entre etapas (e entre vídeos) sem perder nada, e sem gastar limite relendo tudo.

Uso:
  python estado.py PASTA novo --conta auraly-manifestacao --formato prehook-carro
  python estado.py PASTA status                  # etapas, pendências, próxima etapa
  python estado.py PASTA ver CAMINHO             # um pedaço (ex.: takes, foley.0)
  python estado.py PASTA set CAMINHO VALOR       # VALOR em JSON ou texto (ex.: takes.0.custo 12)
  python estado.py PASTA etapa geracao=concluido
  python estado.py PASTA pendencia edicao "porta 1 quadro antes"
  python estado.py PASTA resolver p02
  python estado.py PASTA aprendizado edicao "snap some se colado na porta"   # vai para o caderno da conta
  python estado.py LOTE lote                     # uma linha por vídeo da pasta do dia

Etapas, na ordem do pack: referencia, roteiro, geracao, edicao, qa, entrega.
Status: pendente, em_andamento, aguardando_aprovacao, concluido, nao_precisa.
"""
import json
import sys
from datetime import date
from pathlib import Path

ETAPAS = ["referencia", "roteiro", "geracao", "edicao", "qa", "entrega"]


def carregar(pasta):
    f = Path(pasta) / "estado.json"
    if not f.exists():
        sys.exit(f"sem estado em {pasta}: rode 'novo' primeiro")
    return f, json.loads(f.read_text(encoding="utf-8"))


def salvar(f, e):
    f.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")


def andar(e, caminho, criar=False):
    pai, chave = None, None
    no = e
    for parte in caminho.split("."):
        pai, chave = no, int(parte) if isinstance(no, list) else parte
        if isinstance(no, list):
            no = no[chave]
        else:
            if chave not in no:
                if not criar:
                    sys.exit(f"caminho não existe: {caminho}")
                no[chave] = {}
            no = no[chave]
    return pai, chave, no


def valor(txt):
    try:
        return json.loads(txt)
    except ValueError:
        return txt


def proxima(e):
    return next((n for n in ETAPAS if e["etapas"].get(n) not in ("concluido", "nao_precisa")), None)


def status(pasta, e):
    linhas = [f"{Path(pasta).name}  conta={e.get('conta')}  formato={e.get('formato')}"]
    linhas.append("  " + "  ".join(f"{n}:{e['etapas'].get(n, 'pendente')}" for n in ETAPAS))
    abertas = [p for p in e.get("pendencias", []) if not p.get("resolvida")]
    for p in abertas:
        linhas.append(f"  [{p['id']}] {p['etapa']}: {p['texto']}")
    linhas.append(f"  próxima: {proxima(e) or 'nada, vídeo entregue'}")
    return "\n".join(linhas)


def caderno_da_conta(pasta, conta):
    # sobe a partir da pasta do vídeo até achar contas/<conta>/
    for p in [Path(pasta).resolve(), *Path(pasta).resolve().parents]:
        c = p / "contas" / conta
        if c.is_dir():
            return c / "caderno-criativo.md"
    return Path(pasta) / "caderno-criativo.md"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    pasta, cmd, args = sys.argv[1], sys.argv[2], sys.argv[3:]

    if cmd == "novo":
        f = Path(pasta) / "estado.json"
        if f.exists():
            sys.exit("já existe estado.json nesta pasta")
        o = dict(zip(args[::2], args[1::2]))
        e = {"conta": o.get("--conta"), "formato": o.get("--formato"), "criado": date.today().isoformat(),
             "etapas": {n: "pendente" for n in ETAPAS}, "takes": [], "pendencias": [], "creditos": 0}
        Path(pasta).mkdir(parents=True, exist_ok=True)
        salvar(f, e)
        print(status(pasta, e))
    elif cmd == "lote":
        for d in sorted(p for p in Path(pasta).iterdir() if (p / "estado.json").exists()):
            e = json.loads((d / "estado.json").read_text(encoding="utf-8"))
            ab = sum(1 for p in e.get("pendencias", []) if not p.get("resolvida"))
            print(f"{d.name:40} próxima={proxima(e) or 'entregue':10} pendências={ab}  créditos={e.get('creditos', 0)}")
    else:
        f, e = carregar(pasta)
        if cmd == "status":
            print(status(pasta, e))
        elif cmd == "ver":
            print(json.dumps(andar(e, args[0])[2], ensure_ascii=False, indent=1))
        elif cmd == "set":
            pai, chave, _ = andar(e, args[0], criar=True)
            pai[chave] = valor(args[1])
            salvar(f, e)
            print("ok")
        elif cmd == "etapa":
            n, s = args[0].split("=")
            if n not in ETAPAS:
                sys.exit(f"etapa desconhecida: {n}")
            e["etapas"][n] = s
            salvar(f, e)
            print(status(pasta, e))
        elif cmd == "pendencia":
            pid = f"p{len(e['pendencias']) + 1:02d}"
            e["pendencias"].append({"id": pid, "etapa": args[0], "texto": args[1], "data": date.today().isoformat()})
            salvar(f, e)
            print(pid)
        elif cmd == "resolver":
            for p in e["pendencias"]:
                if p["id"] == args[0]:
                    p["resolvida"] = date.today().isoformat()
            salvar(f, e)
            print(status(pasta, e))
        elif cmd == "aprendizado":
            c = caderno_da_conta(pasta, e.get("conta") or "")
            novo = not c.exists()
            with c.open("a", encoding="utf-8") as h:
                if novo:
                    h.write("# Caderno de criativo\n\nCorreções que valem para outros vídeos. `[ ]` anotado, "
                            "`[x] -> onde entrou`, `[-]` era só daquele vídeo. Nunca apagar linhas.\n\n")
                h.write(f"- [ ] {args[0]} · {args[1]} · {Path(pasta).name} · {date.today().strftime('%d/%m')}\n")
            print(f"anotado em {c}")
        else:
            sys.exit(__doc__)


if __name__ == "__main__":
    main()
