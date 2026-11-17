---
name: entrega-de-criativo
description: Entrega um criativo aprovado - nome padrão do arquivo, capa (thumbnail), cópia para a pasta certa do Drive (pelo Drive montado no computador), parâmetros de rastreio com o nome do anúncio, e preparação do upload pelo conector da Meta (vídeo, texto, título, link com UTM), além da linha no diário de mudanças da conta. Só sobe ou ativa com o "sim" do usuário. Use quando o usuário disser "entrega o vídeo", "sobe pro Drive", "manda pro Drive", "prepara pra subir na Meta", "sobe o anúncio", "registra o criativo", "organiza os criativos".
---

# Entrega de criativo

Um criativo bom que fica perdido numa pasta de testes, sem nome e sem rastreio, não pode ser julgado
pela venda real. Esta skill fecha o ciclo: arquivo organizado, link rastreável e registro.

## Antes de começar
1. Confirme que o vídeo passou na `qa-de-criativo` (ou que o usuário aceitou o ATENÇÃO).
2. Leia `contas/<slug>/criativo.md` e `numeros.md` (fonte de verdade das vendas e parâmetro de origem,
   ex.: `sck` da Hotmart ou `utm_content`).

## 1. Arquivo
- **Nome:** `<CONTA>_<RODADA>_<nome-curto>[_<variação>].mp4`, sem acento e sem espaço (ex.:
  `PSM_VAR_AD05-3D.mp4`, `Liam-Smith_prehook-carro_camisa-preta.mp4`). Versão nova ganha sufixo
  `_v2`, nunca sobrescreve.
- **Capa:** um quadro forte do gancho (nunca preto), salvo como `.jpg` ao lado do vídeo.
- **Drive:** copie para a pasta da conta no Drive montado no computador (ex.: `G:\Meu Drive\...`), que
  sincroniza sozinho. Upload pelo navegador costuma travar; use o disco montado.
- Guarde a receita de montagem ao lado do vídeo no projeto (não precisa ir para o Drive).

## 2. Rastreio
- O nome do anúncio vira o `utm_content` (padrão `gatilho / angulo / H#` do media buying).
- Link do anúncio: destino + `utm_source`, `utm_campaign`, `utm_content` e o parâmetro que a plataforma
  de pagamento guarda (ex.: `sck=<utm_source>|<utm_campaign>|<utm_content>` na Hotmart). É o que deixa
  contar a venda real por anúncio depois (`revisao-meta`).
- Post orgânico: o link de cada conta/perfil é o rastreio; anote qual conta publicou qual vídeo.

## 3. Upload na Meta (só com "sim")
- Pelo conector oficial: subir o vídeo, criar o criativo com texto, título, descrição, CTA e link com
  rastreio, e o anúncio **pausado** no conjunto indicado.
- Mostre o resumo (conjunto, texto, link) e espere o "sim" antes de criar; ativar é outro "sim".
- Se o conector exigir, a capa vai junto como imagem do vídeo.
- Depois de criar, leia de volta e confirme que ficou como aprovado.

## 4. Registro
Uma linha no diário de mudanças da conta (`diario.md`, ou a planilha de controle do produto), no
mesmo dia: data, "criativo novo", nome, onde está, onde subiu, hipótese e data de leitura
(da `rodada-de-teste`).

## Saída
- Caminho no Drive, nome do arquivo e da capa.
- Link final com rastreio.
- O que foi criado na Meta (ou o resumo esperando o "sim").
- A linha registrada no diário.

## Guardrails
- Nada sobe, nada é ativado e nenhuma verba muda sem o "sim" para aquela ação.
- Nunca apagar versão antiga no Drive.
- Não publicar nas redes sociais pelo usuário.
