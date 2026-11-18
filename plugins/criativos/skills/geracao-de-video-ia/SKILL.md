---
name: geracao-de-video-ia
description: Gera as cenas de um vídeo por IA com personagem consistente - Seedance no Dreamina (Omnirreferência com a imagem dos personagens) e Flow do Google (blueprint do avatar, body swap, Omni Flash em modo Elementos) - pelo navegador já logado do usuário, com custo em créditos dito antes de gerar, download de cada cena e conferência da pronúncia pelo whisper contra o roteiro, regerando a cena que falar errado. Use quando o usuário disser "gera as cenas", "faz no Dreamina", "faz no Seedance", "gera no Flow", "cria o avatar", "blueprint do avatar", "body swap", "regera a cena", "baixa os vídeos do Dreamina", "gera em lote", "roda a fila de takes".
---

# Geração de vídeo por IA

Cada geração custa crédito e tempo, e a IA erra de formas previsíveis: troca o rosto, muda a
tatuagem, pronuncia número errado, devolve 16:9 quando a sessão cai. Esta skill gera cena por cena
com o que já se sabe dessas ferramentas e só entrega a cena depois de conferir a fala.

## Antes de começar
1. Leia `contas/<slug>/criativo.md`: ferramenta, imagem de referência (personagens ou blueprint),
   prefixo de estilo, formato, duração e custo por cena. Leia o roteiro aprovado (cenas e
   `falas.json`) da `roteiro-e-copy`.
2. **Custo antes de gerar:** número de cenas x créditos por cena (mais ~30% de margem para regerar).
   Diga o total e espere o "sim". Sem créditos suficientes, pare: comprar é decisão do usuário.
3. Use o navegador em que o usuário já está logado. Se a sessão caiu, peça para ele entrar; nunca
   digite senha.

## 1. Seedance (Dreamina)
- **Configuração** (confira toda vez, porque ela volta ao padrão quando a sessão cai):
  - modelo Seedance 2.0 Mini;
  - Omnirreferência;
  - 9:16;
  - 8 s;
  - o custo exibido (ex.: 224 créditos por cena).
- **Referência:** a imagem dos personagens em toda cena. Se o botão de upload abrir o seletor de
  arquivos do sistema, use um `<input type=file>` próprio e solte o arquivo na área de referência.
- **Prompt:** prefixo de estilo + cena + "diz exatamente esta frase uma vez" + palavra difícil
  repetida. O editor é ProseMirror: limpe o campo (selecionar tudo + apagar) antes de colar, senão
  o texto novo se mistura com o antigo. Confira o texto do campo antes de enviar.
- **Fila:** várias cenas podem ir para a fila de uma vez; acompanhe pela porcentagem.
- **Download:**
  - cada vídeo é identificado pelo texto do prompt que vem antes dele na página;
  - baixe por `fetch` do `src` + blob + `<a download>`;
  - o navegador pode bloquear o 2º download da mesma aba: abra **uma aba nova por vídeo**;
  - confira o arquivo na pasta de downloads antes de seguir.

## 2. Flow (Google)
- **Avatar (uma vez por persona):**
  1. imagem a partir de uma referência real de aparência;
  2. **blueprint de 8 vistas**.
  - Daí em diante, **toda imagem sai do blueprint**, nunca de outra imagem gerada: gerar em cima da
    anterior faz o rosto derivar.
- **Cenário:** body swap com o JSON da foto de referência + blueprint + foto de referência.
- **Roupa:** "não mude nada na imagem, apenas a roupa" + foto da roupa.
- **Tatuagem que mudou:** remova todas e adicione todas de novo a partir do blueprint.
- **Vídeo:** modelo Omni Flash, modo Elementos (Ingredients), imagem da cena como quadro inicial.
  Gere 2 ou 3 versões e escolha os melhores trechos de cada uma.
- **Prompts por take** (duração, velocidade, câmera): use o gerador da conta se existir (ex.: o
  gerador de animação da Appyon) e cole take a take.

## 2b. Modo lote no Flow (menos tokens, mesmos créditos)
Para volume (vários takes por dia), não opere o Flow por print e clique: use `scripts/flow_lote.js`.
Ele roda dentro da aba já logada (Claude in Chrome) e funciona com a interface em inglês ou português.
1. **Fila:** monte `fila.json` com uma linha por take: `{"id": "noah-h1-t1", "refs": ["noah-blueprint.jpg"],
   "prompt": "...", "res": "720p", "dur": "8s"}`. As imagens de referência precisam estar no projeto do Flow.
2. **Injete o script** uma vez na aba do projeto (`javascript_tool` com o conteúdo do arquivo). Recarregou
   a página: injete de novo.
3. **Custo antes:** `await flowLote.configurar({...})` devolve o custo de um take. Some a fila inteira
   (custo × takes × versões) e peça o "sim" para o total. Custos medidos em 2026-11-18 (Omni 1.1 Flash,
   9:16): 360p 4 s = 4, 8 s = 6, 10 s = 7; 720p 4 s = 7, 8 s = 12, 10 s = 15 créditos.
4. **Para cada take, uma chamada só:** `await flowLote.limpar(); for (const r of refs) await
   flowLote.ingrediente(r); await flowLote.preencher(prompt); await flowLote.gerar({limite: N})`.
   `gerar` recusa se o custo passar do limite aprovado ou se faltar crédito, e nunca aprova gasto sozinho.
5. **Acompanhar:** `flowLote.listar()` (sem print) até não haver tile com progresso.
6. **Baixar:** o Chrome só deixa **1 download por aba**. Para cada take, abra uma aba nova no projeto e rode
   só o trecho de download (não precisa injetar tudo):
   `const r=x=>(x.getAttribute('aria-label')||x.textContent||'').trim(); const t=[...document.querySelectorAll('flow-grid-tile-container')][I];
   [...t.querySelectorAll('button')].find(b=>/More options|Mais opções/.test(r(b))).click(); await new Promise(z=>setTimeout(z,600));
   [...document.querySelectorAll('[role=menuitem]')].find(b=>b.textContent.trim().startsWith('download')).click(); await new Promise(z=>setTimeout(z,800));
   [...document.querySelectorAll('[role=menuitem]')].find(b=>r(b).startsWith('720p')).click();`
   Upscale (1080p, 4K) gasta crédito: só com "sim".
7. **Print só no fim**, para conferir o resultado; a pronúncia segue pelo whisper (passo 3).
- **Sinais de que o Flow mudou:** "botão de ajustes não encontrado" ou "opção não encontrada". Aí olhe a
  página uma vez (print ou `read_page`) e ajuste os rótulos no topo do script (bloco `T`).
- **Crédito acaba por conta Google:** cada conta (uma por avatar) tem o seu saldo. O aviso "créditos
  insuficientes" aparece quando o saldo não cobre os ajustes atuais.
- **Não use** os servidores MCP não oficiais do Flow (automatizam com navegador disfarçado e aprovam gasto
  sozinhos): risco para a conta Google, que guarda Drive e e-mail.

## 3. Conferência de cada cena
1. Transcreva com o whisper (idioma da conta) e compare com a fala do roteiro. Rode o
   `qa_video.py --roteiro` da `qa-de-criativo` ou compare palavra por palavra.
2. Palavra trocada (ex.: "equipos" saiu "enquimos", "treinta" saiu "30 de"): reescreva a fala mais
   fácil de pronunciar e **regere só aquela cena**.
3. Confira o visual: personagem igual à referência, sem texto na tela, sem marca d'água, 9:16.
4. Salve como `cena01.mp4`, `cena02.mp4`... na pasta de cenas do projeto. A cena antiga vai para
   `antigas/`, nunca é apagada.

## Saída
- Tabela: cena, prompt usado, créditos gastos, fala conferida (OK ou regerada), arquivo.
- Créditos gastos contra o orçamento aprovado.
- Próximo passo: `edicao-de-video` com a pasta de cenas e o `falas.json`.

## Guardrails
- Nada é gerado sem o "sim" para o custo total.
- Nunca digitar senha, aceitar termos ou comprar crédito pelo usuário.
- Não declarar IA no anúncio se o `marca.md` decidiu assim; seguir as regras da plataforma de vídeo.
- Personagem não pode copiar o rosto de uma pessoa real identificável.
