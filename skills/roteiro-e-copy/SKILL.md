---
name: roteiro-e-copy
description: Escreve o roteiro de um vídeo em blocos (gancho, problema, virada, solução, prova, CTA) e a copy do anúncio ou do post (texto principal, título, descrição, legenda), em português, espanhol LATAM ou inglês, a partir de uma referência, de um anúncio vencedor ou de uma casa do mapa de ângulos, com as falas já escritas para pronúncia por IA (números por extenso) e checadas contra as regras da conta; gera ganchos de 2 linhas em 6 ângulos e passa todo texto pelo humanizador (tira a cara de texto de IA) antes de entregar. Use quando o usuário disser "escreve o roteiro", "roteiro do anúncio", "copy do anúncio", "legenda do post", "adapta esse roteiro", "roteiro em cenas", "versão em espanhol", "copy para o Instagram", "me dá ganchos", "opções de hook", "humaniza esse texto", "tá com cara de IA".
---

# Roteiro e copy

Roteiro bom para IA é diferente de roteiro bom para gente: a IA lê o que está escrito. Esta skill
escreve o roteiro em blocos, divide em cenas do tamanho que a ferramenta gera, deixa cada fala
fácil de pronunciar e entrega junto a copy que vai no anúncio.

## Antes de começar
1. Ache a pasta da conta (`**/contas/<slug>/`) e leia `marca.md` (o que não pode ser dito),
   `criativo.md` (idioma, voz, personagens, duração de cena, e a seção "Voz escrita": palavras
   banidas da conta e padrões de gancho) e `vencedores.md`. Sem `criativo.md`,
   crie a partir de `modelos/criativo.md` com o usuário.
   Onde fica a pasta da conta: primeiro `**/contas/<slug>/` na pasta de trabalho; se não achar, nas
   skills do negócio instaladas (ex.: `~/.claude/skills/appyon-producao/contas/<slug>/`). O negócio
   também pode ter regras de produção próprias (ex.: `appyon-producao`): leia antes de seguir.
2. Defina a base do roteiro: uma ficha da `pesquisa-de-referencias`, um anúncio vencedor (o
   `multiplicador-de-vencedor` diz o que não se mexe) ou uma casa do `mapa-de-angulos`.
3. Defina duração alvo e formato (mini-novela, avatar falando, pre-hook sem fala, VSL curta).

## 1. Roteiro em blocos
| Bloco | Tamanho | Papel |
|---|---|---|
| Gancho | 0 a 3 s | parar o scroll: afirmação forte, ação estranha, número (ver 1b) |
| Problema | 5 a 15 s | a dor ou o medo nas palavras do cliente |
| Virada | 5 a 10 s | por que não é culpa dela / o que ninguém conta |
| Solução | 8 a 15 s | o que o produto faz, de forma concreta (tempo, lugar, formato) |
| Prova | opcional | demonstração ou caso (personagem é ficção, nunca depoimento inventado) |
| CTA | 3 a 5 s | uma ação só, a mesma do botão do anúncio |

## 1b. Ganchos de 2 linhas
Para todo roteiro, gere 6 ganchos antes do resto e valide o gancho com o usuário primeiro: é o
pedaço que decide o teste.
- **Linha 1, abertura:** algo inesperado, específico ou forte. **Linha 2, contraste:** contradiz,
  reenquadra ou corta a abertura por baixo. Até ~40 caracteres por linha (cabe na tela sem quebrar).
- **Um gancho por ângulo:**
  1. número na frente (métrica ou quantidade específica);
  2. contrário (afirma uma crença e vira do avesso);
  3. transformação (antes e depois, com número);
  4. autoridade emprestada (nome, ferramenta, instituição);
  5. confissão (admite um erro ou uma perda);
  6. choque de futuro (algo está prestes a mudar).
- Primeira pessoa em pelo menos uma das linhas, zero hesitação ("talvez", "pode ser que").
- **Pergunta** só quando o `criativo.md` da conta permitir; por padrão, afirmação para mais.
- **Número:** algarismo no texto da tela e na copy ("3 semanas"); **por extenso na fala gerada por
  IA** ("tres semanas"), por causa da pronúncia.
- Números e fatos do gancho saem do produto ou do cliente real; nunca inventar.
- Use os padrões que o `criativo.md` marca como "funciona" e evite os marcados como "não funciona".

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

## 4. Passe humanizador (todo texto, antes da checagem)
Texto com cara de IA perde o leitor e, no orgânico, entrega a conta. Reescreva o roteiro e a copy:
- **Ritmo irregular:** frase de até 6 palavras ao lado de frase de 20 ou mais; parágrafos de tamanhos
  diferentes. Nada de todas as frases com o mesmo comprimento.
- **Sem estrutura de redação:** sem resumo no meio ("como vimos"), sem conclusão anunciada ("em
  resumo", "en resumen", "in short"), sem fim motivacional, sem lista disfarçada ("o primeiro motivo
  é..."). O texto termina no último ponto concreto.
- **Concreto cedo:** um objeto, lugar, número ou nome nas 3 primeiras frases; nome próprio no lugar de
  palavra genérica.
- **Palavras banidas** (no sentido figurado), mais as do `criativo.md` da conta:
  - PT: alavancar, otimizar, potencializar, desbloquear, impulsionar, jornada, ecossistema, sinergia,
    transformador, incrível, revolucionário;
  - ES: potenciar, optimizar, desbloquear, impulsar, viaje (no figurado), ecosistema, sinergia,
    transformador, increíble, revolucionario;
  - EN: leverage, unlock, empower, elevate, journey, ecosystem, synergy, game-changer, delve,
    seamless, transformative.
- **Régua prática:** se soa a post de LinkedIn, troque pela palavra que uma amiga usaria no
  WhatsApp, no idioma e no sotaque da conta.
- **Tom real:** deixe algo ser chato ou difícil quando é verdade (o cansaço, o medo, a dúvida).
  Positividade do começo ao fim é marca de IA.
- **Checklist:** ritmo variado, algo concreto, final em ponto concreto, uma opinião de um lado, uma
  imperfeição humana. Falhou em 2 ou mais: reescreva.

## 5. Checagem antes de entregar
- Sem travessão e sem `{}` em nenhum texto.
- Nada que o `marca.md` proíbe (promessa, credencial, preço riscado inventado).
- Sem atributo pessoal nem alegação de saúde (mesma régua do `mapa-de-angulos`).
- Sem depoimento inventado; caso de personagem fica claramente como história.
- Se o `marca.md` diz para não declarar IA, nenhum texto menciona IA.

## Saída
1. Os 6 ganchos (ângulo, linha 1, linha 2) com o recomendado marcado; o resto do roteiro só depois
   do gancho aprovado, quando o usuário quiser validar em duas etapas.
2. Roteiro em blocos (tabela) com a duração estimada.
3. Cenas numeradas com a fala exata e o prompt de cada uma (prefixo de estilo do `criativo.md` + cena).
4. `falas.json`.
5. Copy: 3 textos, 3 títulos, 3 descrições (ou a legenda do post).
6. Resultado do humanizador e da checagem, item por item.

Grave em `contas/<slug>/roteiros/<AAAA-MM-DD>-<nome>.md` e passe as cenas para a
`geracao-de-video-ia`.

## Guardrails
- Nunca inventar depoimento, número ou resultado.
- Referência de terceiro dá a estrutura; o texto é sempre próprio.
- O usuário aprova o roteiro antes de gastar crédito de geração.
