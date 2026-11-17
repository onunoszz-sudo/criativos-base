# criativos-skills

Pacote de skills do Claude para **produzir criativos**: da referência ao vídeo pronto para subir.
É o irmão do [media-buying-skills](https://github.com/onunoszz-sudo/media-buying-skills). O
media buying decide **o que** testar (`mapa-de-angulos`, `rodada-de-teste`,
`multiplicador-de-vencedor`) e este pack **faz o criativo**.

Repositório privado: o método de algumas contas vem de material de mentoria que não é nosso para
publicar.

## O ciclo de um vídeo
```
mapa-de-angulos / multiplicador (media buying)
        ↓
1 pesquisa-de-referencias → 2 roteiro-e-copy → 3 geracao-de-video-ia → 4 edicao-de-video → 5 qa-de-criativo → 6 entrega-de-criativo
        ↑                                                                                                         ↓
        └──────────────────── revisao-meta / rodada-de-teste leem o resultado pela venda real ←───────────────────┘
```

| Skill | Quando usar | O que entrega |
|---|---|---|
| `pesquisa-de-referencias` | antes de uma rodada, ou com links do mentor | fichas no swipe file: gancho, blocos, duração, ritmo, ângulo, sinal de escala |
| `roteiro-e-copy` | com a referência, o vencedor ou a casa do mapa | roteiro em blocos, cenas com fala escrita para pronúncia, `falas.json`, copy do anúncio ou do post |
| `geracao-de-video-ia` | roteiro aprovado | cenas no Seedance (Dreamina) ou no Flow, com custo aprovado antes e fala conferida |
| `edicao-de-video` | cenas prontas | MP4 final por receita: corte de silêncio, zoom, música por bloco, legenda, faixa, cartão, velocidade, pre-hook |
| `qa-de-criativo` | antes de qualquer upload (e em cada cena) | PASSA / ATENÇÃO / NÃO PASSA por item: formato, primeiro quadro, áudio quebrado, volume, pronúncia |
| `entrega-de-criativo` | vídeo aprovado | arquivo nomeado no Drive, capa, link com rastreio, anúncio pausado na Meta (com "sim"), linha no diário |

## Contexto de cada conta
As skills usam a mesma pasta de conta do media buying, `contas/<slug>/`:
- `marca.md`: o que não pode ser dito (vem do media buying);
- **`criativo.md`** (novo): idioma, voz, personagens, imagem de referência, prefixo de estilo,
  ferramenta, música e o que já deu errado. Modelo em
  `plugins/criativos/skills/roteiro-e-copy/modelos/criativo.md`;
- `cartao.json`: o cartão final da conta (modelo em `edicao-de-video/receitas/cartao-exemplo.json`).

## Scripts (Python 3 + ffmpeg)
| Script | Faz |
|---|---|
| `edicao-de-video/scripts/montar.py receita.json` | montagem de cenas com fala (receitas `mini-novela`, `faixa-sazonal`) |
| `edicao-de-video/scripts/prehook.py receita.json` | pre-hook sem fala (receita `prehook-carro`) |
| `edicao-de-video/scripts/cartao_final.py` | cartão final com a cara do produto |
| `qa-de-criativo/scripts/qa_video.py video.mp4 [--roteiro r.txt]` | QA técnico, só leitura |

Dependências: `ffmpeg`/`ffprobe` no PATH, `pip install pillow faster-whisper`.

## Instalação
```
/plugin marketplace add onunoszz-sudo/criativos-skills
/plugin install criativos@criativos-skills
```
O repositório é privado: a conta do GitHub de quem instala precisa ter acesso. Sem `/plugin`, copie
`plugins/criativos/skills/*` para `~/.claude/skills/`.

## Testado em 2026-11-17
- `montar.py` refez o AD#5 3D do Parto Sin Miedo igual ao aprovado: 38,2 s, mesmos cortes, 99
  palavras de legenda, mesmo cartão.
- `qa_video.py`:
  - reprovou os ganchos H3 e H4 com áudio quebrado (200+ pacotes minúsculos) e aprovou as versões
    corrigidas;
  - acusou "equipos" ouvido como "enquimos" e "todavía" ouvido como "todo había".
- `prehook.py` (receita do pre-hook do carro):
  - validado com trechos do exemplo de referência: headline, bandeiras, riser subindo até 1,9 s,
    música audível a 0,95x e snap com flash no fim;
  - falta rodar com os takes reais do Flow.

## Guardrails (todas as skills)
1. Nada é gerado, sobe ou ativa sem o "sim" para aquela ação e para o custo.
2. Nunca inventar depoimento, número ou resultado; referência dá estrutura, não texto.
3. Toda imagem de personagem sai da referência fixa (blueprint).
4. Nunca apagar versão antiga: versão nova ganha sufixo.
5. O Claude não digita senha, não aceita termos e não compra crédito.
