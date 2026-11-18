---
name: edicao-de-video
description: Monta e edita o vídeo final por script (ffmpeg), sem abrir editor - corta o silêncio de cada cena, zoom alternado, música por bloco com ducking, legenda palavra por palavra, faixa no topo, cartão final com a cara do produto, velocidade e áudio a -14 LUFS - a partir de uma receita JSON; sons de cada ação presos ao quadro e níveis copiados da referência camada por camada em vídeo sem fala; estado de cada vídeo do lote num arquivo (estado.py) e caderno de aprendizados da conta. As receitas de cada negócio ficam no plugin do negócio (appyon-prehook, goofy-montagem). Use quando o usuário disser "monta o vídeo", "edita o vídeo", "junta as cenas", "corta os silêncios", "põe música", "põe legenda", "deixa mais rápido", "acelera 15%", "troca o cartão final", "versão Black Friday com faixa".
---

# Edição de vídeo

Edição por script repete o mesmo resultado toda vez e não esquece um passo. Esta skill escolhe a
receita, preenche o JSON e roda os scripts da pasta `scripts/`.

## Antes de começar
1. Leia `contas/<slug>/criativo.md` (cartão, música, idioma) e confira a pasta de cenas e o
   `falas.json` da `roteiro-e-copy`/`geracao-de-video-ia`.
   Onde fica a pasta da conta: primeiro `**/contas/<slug>/` na pasta de trabalho; se não achar, nas
   skills do negócio instaladas (ex.: `~/.claude/skills/appyon-producao/contas/<slug>/`). O negócio
   também pode ter regras de produção próprias (ex.: `appyon-producao`): leia antes de seguir.
2. Precisa de `ffmpeg`/`ffprobe` no PATH, Python 3 com `Pillow`, e `faster-whisper` quando há fala.
3. Trabalhe numa pasta local (não dentro de pasta sincronizada do Drive); copie para o Drive só o final.

## Scripts
| Script | Para quê |
|---|---|
| `scripts/montar.py receita.json` | vídeo a partir de cenas com fala: corta silêncio, zoom, música por bloco, legenda, faixa, cartão, velocidade |
| `scripts/estado.py PASTA status` | onde cada vídeo está (etapas, pendências, créditos); `lote` resume a pasta do dia |
| `scripts/cartao_final.py fundo.jpg saida.png 720 1280 cartao.json` | só o cartão final (o `montar.py` já chama) |

O cabeçalho de cada script documenta todos os campos da receita.

## Receitas
- **`cartao-exemplo.json`:** campos do cartão final.
- As receitas de formato ficam no plugin de cada negócio, porque são o método dele:
  - Goofy: `goofy-montagem` (mini-novela, faixa sazonal);
  - Appyon: `appyon-prehook` (pre-hook do carro, com o `prehook.py`).
- Copie a receita para a pasta do vídeo, ajuste caminhos e textos, e rode.

## Estado do vídeo e do lote (economiza limite)
Em volume (vários vídeos por dia), a memória fica em arquivo, não na conversa:
1. Cada vídeo tem uma pasta com `estado.json`: `estado.py PASTA novo --conta <slug> --formato <receita>`.
2. Cada etapa grava o que decidiu (`set`, `etapa geracao=concluido`) e o que ficou pendente (`pendencia`).
3. Para retomar, rode `estado.py PASTA status` em vez de reler arquivos ou o histórico; `estado.py
   PASTA_DO_DIA lote` mostra todos os vídeos do dia numa linha cada.
4. Fechou uma etapa com tudo aplicado: pode limpar o chat (`/clear`). Nunca limpe com pedido do
   usuário que não foi aplicado nem anotado como pendência.
5. Etapas mecânicas (baixar, organizar, rodar QA) podem rodar num modelo mais leve; roteiro, edição
   e revisão de som pedem o mais capaz.

## Caderno de aprendizados da conta
Toda correção do usuário que vale **para outros vídeos** vira uma linha no caderno da conta, na hora:
`estado.py PASTA aprendizado <etapa> "<o que foi pedido>"` (grava em `contas/<slug>/caderno-criativo.md`).
- "tira essa frase" é só deste vídeo: não anota. Na dúvida, anota com "(talvez só deste vídeo)".
- Anotar não muda nada. Quando o usuário pedir "aplica os aprendizados": proponha onde cada linha
  entra (gosto da conta vai para o `criativo.md`; ofício que vale para tudo vai para a skill), ele
  filtra, você grava e marca `[x] -> onde entrou` ou `[-]`.

## Sons de ação (é o que segura a retenção em vídeo sem fala)
Os sons das ações são tão importantes quanto a imagem (ex.: tampa do pote abrindo, tapete levantando,
tapete caindo, mão alisando o tapete, porta batendo). Vídeo de IA quase sempre vem sem eles ou baixos
demais. Por isso:
1. **Liste cada ação visível da referência e o som que ela tem.** Na `pesquisa-de-referencias`,
   anote os sons junto com os cortes.
2. **Ache o som de cada ação** nos takes (inclusive nos não usados) com o espectrograma
   (`showspectrumpic`) e o RMS a cada 0,05 s: estalo é uma linha vertical. Recorte com 0,1 s de folga.
3. **Prenda o som ao quadro da ação**: no bloco `foley`, `ancora` é o instante do estalo no arquivo
   do som e `ponto` é o quadro da ação na cena (tempo do arquivo da cena). O script converte para o
   tempo do vídeo final, já com a velocidade.
4. **Prefira o trecho em que imagem e som vêm do mesmo take**: o som já cai no quadro certo. Junte trechos de takes diferentes quando um deles tem a física mais realista.
5. **Ação com som fica em 1x**; acelerar o trecho distorce o som.
6. **Dois sons fortes nunca no mesmo instante** (ex.: porta batendo em cima do snap): o mais fraco
   some. Deixe pelo menos 0,2 s entre eles.
7. **Não invente som sintético** de ação (areia, canela caindo): chiado falso soa pior do que
   silêncio. Sem som real, deixe sem.
8. **Um protagonista por momento:** no máximo 3 camadas por evento (principal, grave por baixo só nos
   momentos fortes, um agudo curto de apoio), cada uma numa faixa de frequência diferente.
9. **Respiro antes do impacto:** nada de outros sons nos ~0,5 s antes do som mais forte; o riser
   termina no evento e corta seco.
10. **Sincronia:** impacto com o transiente no quadro do evento; whoosh com o **pico** no quadro da
    troca, não no começo do movimento; um som pode vir 1 quadro adiantado.
11. **Não repita o mesmo arquivo** de efeito em menos de ~20 s; varie a intensidade ao longo do vídeo.

## Níveis: iguais aos da referência
Vídeo sem fala não se normaliza para -14 LUFS. Meça a referência camada por camada e copie para o bloco
`niveis` (RMS de (L+R)/2, janela de 0,1 s para pico):
- `riser_rms_inicio`: riser sozinho, antes do primeiro som (ex.: 0 a 0,45 s);
- `musica_rms`: trecho só com música; se tiver ASMR por baixo, desconte comparando com o original;
- `foley_pico`: o som de ação mais forte;
- `snap_pico`: o snap.

O script do formato ajusta cada camada para bater no alvo e mostra o ganho aplicado (ex.: o
`prehook.py` da Appyon). Cuidado: o `-ac 1` do ffmpeg mede 3 dB acima de (L+R)/2.

## Regras de edição que valem sempre
- **Primeiro quadro nunca preto** e o vídeo começa no primeiro movimento ou na primeira palavra.
- **Sem silêncio parado:** 0,12 s antes da primeira palavra e 0,30 s depois da última.
- **Velocidade** entre 1,10 e 1,15 para deixar mais dinâmico; acima disso a voz soa artificial.
- **Áudio final a -14 LUFS** nos vídeos com fala (música abaixo da voz, com ducking); no vídeo sem fala vale o nível da referência (acima).
- **Faixa e legenda** fora da área do botão do Reels e da legenda do post (meio-baixo da tela).
- **Cartão final:** com a cara do produto (marca, chamada, botão apontando para o botão real), nunca
  um fundo liso "toca em mais informação".
- **Erros que os scripts já evitam** (não mexer):
  - `fps=30` antes do zoompan: sem isso, cena de 24 fps acelera e perde a sincronia da boca;
  - altura do vídeo é `ih` no drawbox, não `h`;
  - cena sem áudio ganha silêncio, para o concat não quebrar.
- Mudar uma coisa (velocidade, cartão, música) é mudar a receita e rodar de novo; nunca editar o
  MP4 final por cima.

## Saída
- O MP4 final (720x1280 ou 1080x1920), a duração e o caminho; `estado.json` atualizado.
- A receita usada, salva ao lado do vídeo (é o que permite refazer igual).
- Próximo passo obrigatório: `qa-de-criativo` no arquivo final.

## Guardrails
- Música de terceiros só com a alteração da receita (velocidade e tom) e sabendo do risco; música
  livre de direitos é sempre a opção mais segura.
- O vídeo antigo não é apagado nem sobrescrito sem o "sim" do usuário: salve com sufixo de versão.
- **Mudou um script que já funciona?** Rode de novo a receita de um vídeo aprovado e compare com o
  aprovado (ex.: md5 do áudio). Mudança que ninguém pediu é bug.
