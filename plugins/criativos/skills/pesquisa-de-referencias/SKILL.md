---
name: pesquisa-de-referencias
description: Acha e destrincha vídeos de referência para anúncios e posts - busca na Biblioteca de Anúncios da Meta (frase exata, tempo no ar), em perfis indicados do Instagram e TikTok e no YouTube, transcreve (legenda grátis ou whisper local) e decompõe cada vídeo em gancho, blocos, duração, ritmo de corte, formato e CTA, gravando no swipe file do nicho. Use quando o usuário disser "acha referências", "pesquisa vídeos de referência", "espiona os concorrentes", "o que está rodando no nicho", "destrincha esse vídeo", "garimpo", "spy de criativo", ou mandar links de vídeos para analisar.
---

# Pesquisa de referências

O anúncio que roda há semanas já passou no teste do leilão. Esta skill encontra esses vídeos,
separa a estrutura (o que dá para reaproveitar) do texto (o que não se copia) e guarda tudo num
lugar que a `roteiro-e-copy` consegue ler depois.

## Antes de começar
1. Ache a pasta da conta (`**/contas/<slug>/`) e leia `marca.md`, `criativo.md` (idioma, formato) e
   `angulos.md` se existir (casas vazias do mapa de ângulos dizem o que procurar).
2. Defina com o usuário: nicho, idioma, país, formato (vídeo curto, VSL, animação, avatar falando) e
   quantos vídeos (padrão 10). Se ele mandou links, comece por eles.

## 1. Onde procurar (nesta ordem)
1. **Links do usuário ou do mentor:** são a referência mais valiosa; analisar todos.
2. **Biblioteca de Anúncios da Meta** (pelo navegador já logado):
   - busca por **frase exata** entre aspas, país e "todos os anúncios";
   - **sinal de escala:** anúncio ativo há 21+ dias, várias versões do mesmo criativo, várias páginas
     com o mesmo vídeo;
   - anote a página, a data de início e quantas versões existem.
3. **Instagram e TikTok:** perfis indicados e busca pelas palavras-chave do nicho; sinal de alcance é
   visualização muito acima da média do perfil.
4. **YouTube:** para VSL longa e roteiros; a legenda automática sai grátis.

## 2. Baixar e transcrever
- Guarde cada vídeo numa pasta própria de referências (nunca dentro de pasta sincronizada do Drive
  enquanto processa).
- **Transcrição grátis primeiro:**
  - YouTube: `yt-dlp --skip-download --write-auto-subs --sub-langs "<idioma>.*"`;
  - vídeo baixado: whisper local (`faster-whisper`, modelo small, `word_timestamps=True`).
- Se o download não for possível, trabalhe com o que a página mostra (texto, duração, quadros) e
  diga o que faltou.

## 3. Destrinchar (uma ficha por vídeo)
| Campo | O que anotar |
|---|---|
| Fonte | link, página/perfil, data de início, tempo no ar, versões |
| Formato | UGC, avatar IA falando, animação, demonstração, estático, tela dividida |
| Duração e ritmo | segundos totais, número de cortes, corte médio em segundos |
| Gancho (0 a 3 s) | o que se vê e o que se ouve; tipo: pergunta, afirmação forte, ação estranha, número |
| Blocos | gancho → problema → virada → solução → prova → CTA, com o segundo de início de cada um |
| Ângulo | dor, medo, desejo, objeção ou identidade (mesma régua do `mapa-de-angulos`) |
| Prova | depoimento, demonstração, autoridade, número |
| CTA | o que pede e onde aponta (link, comentário, quiz) |
| Áudio | voz, música, efeitos; legenda queimada ou não |
| O que dá para levar | a estrutura, em uma linha, sem o texto original |

## Saída
Sem travessão, palavras simples.
1. **Uma linha:** quantos vídeos, de onde, quantos com sinal de escala.
2. **Tabela resumo:** um vídeo por linha (fonte, formato, duração, gancho, ângulo, tempo no ar).
3. **Padrões:** o que se repete entre os que escalaram (duração, gancho, ordem dos blocos).
4. **Fichas** completas.
5. **Sugestão:** as 3 estruturas para levar à `roteiro-e-copy`.

Grave as fichas em `biblioteca/swipe-files/<nicho>.md` (ou `contas/<slug>/referencias.md`),
acrescentando com data, sem apagar as antigas.

## Guardrails
- Referência mostra estrutura; o texto, a voz e a imagem de terceiros não vão para o anúncio.
- Nunca baixar nem republicar o vídeo de outra pessoa como se fosse nosso.
- Dado pessoal de quem aparece nos vídeos não vai para o swipe file.
- Não fazer login, não aceitar termos nem pagar ferramenta de spy sem o "sim" do usuário.
