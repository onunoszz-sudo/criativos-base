---
name: edicao-de-video
description: Monta e edita o vídeo final por script (ffmpeg), sem abrir editor - corta o silêncio de cada cena, zoom alternado, música por bloco com ducking, legenda palavra por palavra, faixa no topo, cartão final com a cara do produto, velocidade e áudio a -14 LUFS - a partir de uma receita JSON; tem receitas prontas de mini-novela, anúncio com faixa sazonal e pre-hook sem fala (riser, música a 0,95x com tom alterado, headline, bandeiras, snap com flash). Use quando o usuário disser "monta o vídeo", "edita o vídeo", "junta as cenas", "corta os silêncios", "põe música", "põe legenda", "deixa mais rápido", "acelera 15%", "troca o cartão final", "faz o pre-hook", "versão Black Friday com faixa".
---

# Edição de vídeo

Edição por script repete o mesmo resultado toda vez e não esquece um passo. Esta skill escolhe a
receita, preenche o JSON e roda os scripts da pasta `scripts/`.

## Antes de começar
1. Leia `contas/<slug>/criativo.md` (cartão, música, idioma) e confira a pasta de cenas e o
   `falas.json` da `roteiro-e-copy`/`geracao-de-video-ia`.
2. Precisa de `ffmpeg`/`ffprobe` no PATH, Python 3 com `Pillow`, e `faster-whisper` quando há fala.
3. Trabalhe numa pasta local (não dentro de pasta sincronizada do Drive); copie para o Drive só o final.

## Scripts
| Script | Para quê |
|---|---|
| `scripts/montar.py receita.json` | vídeo a partir de cenas com fala: corta silêncio, zoom, música por bloco, legenda, faixa, cartão, velocidade |
| `scripts/prehook.py receita.json` | pre-hook curto sem fala: trechos acelerados, riser, música com tom alterado, headline, bandeiras, snap com flash |
| `scripts/cartao_final.py fundo.jpg saida.png 720 1280 cartao.json` | só o cartão final (o `montar.py` já chama) |

O cabeçalho de cada script documenta todos os campos da receita.

## Receitas prontas (`receitas/`)
- **`mini-novela.json`:** cenas de 8 s com diálogo, música em 3 blocos (tensão, virada, final),
  legenda palavra por palavra, cartão do produto e velocidade 1,15.
- **`faixa-sazonal.json`:** a mesma montagem mais uma faixa fixa no topo (ex.: "BLACK NOVEMBER"),
  posicionada para não cobrir balão de fala nem legenda.
- **`prehook-carro.json`:** pre-hook de ~6 s sem fala:
  - começa no primeiro movimento;
  - trechos parados acelerados;
  - riser desde o 1º quadro (-12 dB);
  - música entrando no fim do riser, com fade de 0,35 s, a 0,95x com o tom alterado (evita bloqueio
    de direito autoral);
  - headline branca com contorno e bandeiras;
  - snap com flash nos últimos 0,4 s.
- **`cartao-exemplo.json`:** campos do cartão final.

Copie a receita para a pasta do projeto, ajuste caminhos e textos, e rode.

## Regras de edição que valem sempre
- **Primeiro quadro nunca preto** e o vídeo começa no primeiro movimento ou na primeira palavra.
- **Sem silêncio parado:** 0,12 s antes da primeira palavra e 0,30 s depois da última.
- **Velocidade** entre 1,10 e 1,15 para deixar mais dinâmico; acima disso a voz soa artificial.
- **Áudio final a -14 LUFS**; música abaixo da voz (ducking).
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
- O MP4 final (720x1280 ou 1080x1920), a duração e o caminho.
- A receita usada, salva ao lado do vídeo (é o que permite refazer igual).
- Próximo passo obrigatório: `qa-de-criativo` no arquivo final.

## Guardrails
- Música de terceiros só com a alteração da receita (velocidade e tom) e sabendo do risco; música
  livre de direitos é sempre a opção mais segura.
- O vídeo antigo não é apagado nem sobrescrito sem o "sim" do usuário: salve com sufixo de versão.
