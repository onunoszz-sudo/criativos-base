# criativos-base

A base de skills do Claude para **produzir criativos**, comum a todos os negócios: da referência ao
vídeo pronto para subir. O método de cada negócio fica num repositório próprio, que instala junto
com esta base:

| Repositório | O que tem | Quem acessa |
|---|---|---|
| **criativos-base** (este) | as 6 skills do ciclo, scripts de montagem, QA, Flow em lote, estado do lote | todos |
| [criativos-appyon](https://github.com/onunoszz-sudo/criativos-appyon) | pre-hook do carro, manual de produção, prompts, contas do Auraly | Pedro e o time da Appyon |
| [criativos-goofy](https://github.com/onunoszz-sudo/criativos-goofy) | receitas de anúncio (mini-novela, faixa sazonal), contas da Goofy | Pedro e o time da Goofy |

Novo negócio: um repositório `criativos-<negocio>` copiado da estrutura da Appyon, com o
`marketplace.json` apontando para esta base. Nada de método de negócio entra aqui.

Repositórios privados: o método de algumas contas vem de material de mentoria que não é nosso para
publicar. O GitHub dá acesso por repositório inteiro, por isso cada negócio tem o seu.

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
| `pesquisa-de-referencias` | antes de uma rodada, ou com links do mentor | fichas no swipe file: gancho, blocos, cortes, mapa de sons, níveis |
| `roteiro-e-copy` | com a referência, o vencedor ou a casa do mapa | roteiro em blocos, ganchos de 2 linhas, passe humanizador, `falas.json`, copy |
| `geracao-de-video-ia` | roteiro aprovado | cenas no Seedance (Dreamina) ou no Flow (modo lote), com custo aprovado antes e fala conferida |
| `edicao-de-video` | cenas prontas | MP4 final por receita, sons de ação no quadro, estado do vídeo, caderno de aprendizados |
| `qa-de-criativo` | antes de qualquer upload | PASSA / ATENÇÃO / NÃO PASSA: formato, primeiro quadro, áudio quebrado, volume, pronúncia, sons |
| `entrega-de-criativo` | vídeo aprovado | arquivo nomeado no Drive, capa, link com rastreio, anúncio pausado na Meta (com "sim") |

## Contexto de cada conta
As skills procuram `contas/<slug>/`: primeiro na pasta de trabalho, depois na skill de contas do
negócio instalado (ex.: `appyon-producao/contas/`).
- `criativo.md`: idioma, voz, voz escrita, personagens, referência, ferramenta, música, o que deu errado
  (modelo em `skills/roteiro-e-copy/modelos/criativo.md`);
- `caderno-criativo.md`: correções do usuário que valem para outros vídeos (gravado pelo `estado.py`);
- `cartao.json`: o cartão final (modelo em `skills/edicao-de-video/receitas/cartao-exemplo.json`);
- `marca.md`: o que não pode ser dito (do pack de media buying).

## Scripts (Python 3 + ffmpeg)
| Script | Faz |
|---|---|
| `edicao-de-video/scripts/montar.py receita.json` | montagem de cenas com fala |
| `edicao-de-video/scripts/cartao_final.py` | cartão final com a cara do produto |
| `edicao-de-video/scripts/estado.py PASTA status` | estado de cada vídeo e do lote do dia |
| `geracao-de-video-ia/scripts/flow_lote.js` | Flow em lote dentro da aba logada (custo, limite, saldo, download do original) |
| `qa-de-criativo/scripts/qa_video.py video.mp4 [--roteiro r.txt]` | QA técnico, só leitura |

Dependências: `ffmpeg`/`ffprobe` no PATH, `pip install pillow faster-whisper numpy`.

## Instalação
Quem trabalha num negócio instala o marketplace **do negócio**, que já traz esta base:
```
/plugin marketplace add onunoszz-sudo/criativos-appyon
/plugin install criativos@criativos-appyon
/plugin install appyon@criativos-appyon
```
Só a base: `/plugin marketplace add onunoszz-sudo/criativos-base` e `/plugin install criativos@criativos-base`.
A conta do GitHub de quem instala precisa ter acesso aos repositórios. Sem `/plugin`, copie
`skills/*` daqui e do repositório do negócio para `~/.claude/skills/`.

## Economia de limite em volume
- Um vídeo por pasta, com `estado.json`; retome pelo `estado.py status`, não pelo histórico.
- Limpe o chat (`/clear`) entre etapas fechadas; o estado guarda tudo.
- Flow e Dreamina em lote por script na aba logada, sem print a cada clique; print só no fim.
- Etapas mecânicas num modelo mais leve; roteiro, edição e som no mais capaz.

## Guardrails (todas as skills)
1. Nada é gerado, sobe ou ativa sem o "sim" para aquela ação e para o custo.
2. Nunca inventar depoimento, número ou resultado; referência dá estrutura, não texto.
3. Toda imagem de personagem sai da referência fixa (blueprint).
4. Nunca apagar versão antiga: versão nova ganha sufixo.
5. O Claude não digita senha, não aceita termos e não compra crédito.
6. Método de negócio fica no repositório do negócio, nunca nesta base.
