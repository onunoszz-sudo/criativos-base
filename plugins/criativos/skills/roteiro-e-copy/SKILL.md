---
name: roteiro-e-copy
description: Escreve o roteiro de um vídeo em blocos (gancho, problema, virada, solução, prova, CTA) e a copy do anúncio ou do post (texto principal, título, descrição, legenda), em português, espanhol LATAM ou inglês, a partir de uma referência, de um anúncio vencedor ou de uma casa do mapa de ângulos, com as falas já escritas para pronúncia por IA (números por extenso) e checadas contra as regras da conta. Use quando o usuário disser "escreve o roteiro", "roteiro do anúncio", "copy do anúncio", "legenda do post", "adapta esse roteiro", "roteiro em cenas", "versão em espanhol", "copy para o Instagram".
---

# Roteiro e copy

Roteiro bom para IA é diferente de roteiro bom para gente: a IA lê o que está escrito. Esta skill
escreve o roteiro em blocos, divide em cenas do tamanho que a ferramenta gera, deixa cada fala
fácil de pronunciar e entrega junto a copy que vai no anúncio.

## Antes de começar
1. Ache a pasta da conta (`**/contas/<slug>/`) e leia `marca.md` (o que não pode ser dito),
   `criativo.md` (idioma, voz, personagens, duração de cena) e `vencedores.md`. Sem `criativo.md`,
   crie a partir de `modelos/criativo.md` com o usuário.
2. Defina a base do roteiro: uma ficha da `pesquisa-de-referencias`, um anúncio vencedor (o
   `multiplicador-de-vencedor` diz o que não se mexe) ou uma casa do `mapa-de-angulos`.
3. Defina duração alvo e formato (mini-novela, avatar falando, pre-hook sem fala, VSL curta).

## 1. Roteiro em blocos
| Bloco | Tamanho | Papel |
|---|---|---|
| Gancho | 0 a 3 s | parar o scroll: pergunta, afirmação forte, ação estranha |
| Problema | 5 a 15 s | a dor ou o medo nas palavras do cliente |
| Virada | 5 a 10 s | por que não é culpa dela / o que ninguém conta |
| Solução | 8 a 15 s | o que o produto faz, de forma concreta (tempo, lugar, formato) |
| Prova | opcional | demonstração ou caso (personagem é ficção, nunca depoimento inventado) |
| CTA | 3 a 5 s | uma ação só, a mesma do botão do anúncio |

## 2. Cenas (para geração por IA)
- Uma cena por fala ou ação, do tamanho que a ferramenta gera (ex.: 8 s no Seedance). Fala de até
  ~20 palavras por cena de 8 s.
- Cada cena: lugar, quem está, ação, enquadramento, a fala exata entre aspas e quem fala.
- **Escrita para pronúncia:**
  - números por extenso ("treinta semanas", "quince a veinte minutos"), nunca algarismo;
  - sem sigla que a voz soletre errado; sem símbolo (%, $, /) dentro da fala;
  - palavra difícil repetida no fim do prompt ("pronouncing 'equipos' clearly");
  - "diz exatamente esta frase uma vez" no prompt.
- Gere também o `falas.json` (`{"cena01": "fala exata", ...}`) que a `edicao-de-video` usa para
  cortar silêncio e legendar.

## 3. Copy do anúncio ou do post
- **Texto principal:** 3 versões (curta de 1 a 2 linhas, média, longa com bullets), a primeira linha
  repete o gancho.
- **Título** (até 40 caracteres) e **descrição** (até 30), em 3 versões.
- **Post orgânico:** legenda com gancho na primeira linha, CTA para o link da bio ou comentário fixado.
- Mesmo idioma e tratamento do `criativo.md`.

## 4. Checagem antes de entregar
- Sem travessão e sem `{}` em nenhum texto.
- Nada que o `marca.md` proíbe (promessa, credencial, preço riscado inventado).
- Sem atributo pessoal nem alegação de saúde (mesma régua do `mapa-de-angulos`).
- Sem depoimento inventado; caso de personagem fica claramente como história.
- Se o `marca.md` diz para não declarar IA, nenhum texto menciona IA.

## Saída
1. Roteiro em blocos (tabela) com a duração estimada.
2. Cenas numeradas com a fala exata e o prompt de cada uma (prefixo de estilo do `criativo.md` + cena).
3. `falas.json`.
4. Copy: 3 textos, 3 títulos, 3 descrições (ou a legenda do post).
5. Resultado da checagem, item por item.

Grave em `contas/<slug>/roteiros/<AAAA-MM-DD>-<nome>.md` e passe as cenas para a
`geracao-de-video-ia`.

## Guardrails
- Nunca inventar depoimento, número ou resultado.
- Referência de terceiro dá a estrutura; o texto é sempre próprio.
- O usuário aprova o roteiro antes de gastar crédito de geração.
