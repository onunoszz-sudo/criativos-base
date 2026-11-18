---
name: qa-de-criativo
description: Confere um vídeo de anúncio ou post antes de subir e devolve PASSA, ATENÇÃO ou NÃO PASSA por item - formato 9:16, duração, primeiro quadro preto, quadros pretos no meio, áudio quebrado no gancho (pacotes minúsculos e silêncio digital, defeito típico de gancho colado por IA), volume, pronúncia contra o roteiro pelo whisper, área segura do Reels, legenda, cartão final e checagem de política. Só lê, não altera o arquivo. Use quando o usuário disser "confere o vídeo", "QA do criativo", "pode subir?", "checa o áudio", "a fala saiu certa?", "revisa antes de publicar".
---

# QA de criativo

Um vídeo com gancho mudo ou palavra trocada perde o dinheiro do teste inteiro, e esses defeitos não
aparecem numa olhada rápida. Esta skill roda as checagens técnicas por script e as visuais por
amostra de quadros, antes de qualquer upload.

## Antes de começar
1. Pegue o arquivo final e, se houver fala, o roteiro (`falas.json` juntado em um `.txt`, na ordem).
2. Leia `contas/<slug>/marca.md` (o que não pode aparecer) e `criativo.md` (idioma, duração alvo).

## 1. Checagem técnica (script)
```
python scripts/qa_video.py video.mp4 --roteiro roteiro.txt --idioma es --max 90
```
| Item | Regra |
|---|---|
| Formato | 9:16, pelo menos 720 px de largura |
| Duração | dentro do alvo da conta |
| Primeiro quadro | brilho médio acima de 20 (não preto) |
| Quadros pretos no meio | nenhum trecho preto de 0,3 s ou mais |
| Áudio do gancho | no máximo 1 pacote de áudio < 0,01 s nos 3 primeiros segundos e nenhum silêncio digital (< -60 dB) de 1,2 s+ nos 5 primeiros |
| Volume | -14 LUFS (±3) nos vídeos com fala; no pre-hook, `--lufs` com o valor da referência |
| Pronúncia | palavras do roteiro que não aparecem na fala; número por extenso contra algarismo não conta como erro |

O script devolve código 1 quando algo NÃO PASSA. Rode também em cada cena gerada, antes da montagem:
é mais barato regerar uma cena do que remontar o vídeo.

## 2. Checagem visual (amostra de quadros)
Extraia um quadro a cada 2 a 3 s e o último (`ffmpeg -vf fps=0.5,scale=240:-1,tile=6x2`) e olhe:
- personagem igual em todas as cenas (rosto, roupa, tatuagem);
- nenhum texto, marca d'água ou selo de IA indesejado;
- legenda legível e fora da área do botão e da legenda do post do Reels (faixa de baixo ~20% e lateral
  direita);
- faixa do topo sem cobrir rosto ou balão de fala;
- cartão final com o texto inteiro dentro dos limites e coerente com a oferta (mesmo preço, mesmo CTA).

## 2b. Sons de ação (pre-hook e vídeo sem fala)
Com o mapa de sons da referência (`pesquisa-de-referencias`), confira no espectrograma
(`ffmpeg -i video.mp4 -lavfi showspectrumpic=s=1200x400:scale=log:fscale=log esp.png`):
- cada ação visível tem o seu som, no quadro da ação (estalo = linha vertical);
- nenhum som forte encobre outro (snap e porta no mesmo instante, por exemplo);
- nada de chiado sintético no lugar de um som real.
Faltou som de ação que a referência tem: NÃO PASSA.

## 3. Checagem de conteúdo
- Nada proibido pelo `marca.md` (promessa, credencial, preço).
- Sem atributo pessoal nem alegação de saúde (régua do `mapa-de-angulos`).
- CTA do vídeo igual ao botão do anúncio e ao destino (quiz, link da bio).

## Saída
1. **Resultado:** PASSA, PASSA COM ATENÇÃO ou NÃO PASSA.
2. Lista item por item com o valor medido.
3. Para cada NÃO PASSA: o conserto e a skill que faz (regerar cena na `geracao-de-video-ia`, mudar a
   receita na `edicao-de-video`, reescrever fala na `roteiro-e-copy`).

## Guardrails
- Só lê. Não corrige o arquivo, não sobe nada.
- Vídeo com NÃO PASSA não vai para a `entrega-de-criativo` sem o "sim" explícito do usuário sabendo
  do defeito.
