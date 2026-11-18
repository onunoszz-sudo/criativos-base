// Modo lote do Google Flow (flow.google.com), rodando na aba já logada do usuário pelo Claude in Chrome.
// Funciona com a interface em inglês ou em português (cada conta Google pode estar num idioma).
// Injete o arquivo inteiro uma vez por aba (javascript_tool); a cada recarga da página, injete de novo.
// Depois chame só as funções curtas:
//   await flowLote.estado()                         -> ajustes atuais, custo da próxima geração, crédito
//   await flowLote.configurar({tipo:'Video', modo:'Ingredients', proporcao:'9:16', res:'720p', dur:'8s', qtd:'x1'})
//        (em português: tipo 'Vídeo', modo 'Elementos'; res, dur, proporção e qtd são iguais)
//   await flowLote.custo()                          -> créditos que a próxima geração vai usar
//   await flowLote.ingrediente('noah-blueprint.jpg')-> põe uma imagem do projeto como referência no prompt
//   await flowLote.preencher('prompt da cena')      -> escreve o prompt (substitui o anterior)
//   await flowLote.gerar({limite: 15})              -> só clica em gerar se custo <= limite e houver crédito
//   flowLote.listar()                               -> tiles do projeto: índice, tipo, título, progresso
//   await flowLote.baixar(0)                        -> baixa o tile em 720p (1 download por aba: aba nova a cada um)
// Nenhuma função aprova gasto sozinha: o limite de créditos vem do "sim" do usuário para o lote.
(() => {
  const T = {   // rótulos em inglês | português
    ajustes: /Settings trigger|Gatilho de configura/,
    mais: /More options|Mais opções/,
    gerar: /Start generation|Iniciar geração/,
    semCredito: /Insufficient credits|cr[ée]ditos insuficientes/i,
    avisoCredito: /Not enough credits|cr[ée]ditos suficientes|cr[ée]ditos insuficientes/i,
    botaoAjustesDoAviso: /^(Settings|Configurações)$/,
    custo: /(\d+)\s*(credits?|cr[ée]ditos?)/,
    titulo: /More options|Mais opções|Reuse prompt|Reutilizar comando|Favorite|Favorito/,
    limpar: /^(Clear prompt|Apagar comando)$/,
  };
  const esperar = ms => new Promise(r => setTimeout(r, ms));
  const rot = x => (x.getAttribute('aria-label') || x.textContent || '').trim().replace(/\s+/g, ' ');
  const botoes = (raiz = document) => [...raiz.querySelectorAll('button,[role=menuitem],[role=radio],[role=tab],[role=option]')];
  const acha = (re, raiz) => botoes(raiz).find(b => re.test(rot(b)));
  const termina = (txt, raiz) => botoes(raiz).find(b => rot(b).replace(/info$/, '').endsWith(txt));   // "360pinfo"
  const pop = () => [...document.querySelectorAll('.cdk-overlay-pane')].pop();
  const esc = () => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  const itensMenu = () => botoes(document).filter(b => b.getAttribute('role') === 'menuitem');

  async function abrirAjustes() {
    const t = acha(T.ajustes);
    if (!t) throw new Error('botão de ajustes não encontrado (a página carregou? mudou?)');
    const aberto = () => pop() && /9:16|16:9/.test(pop().innerText) && T.custo.test(pop().innerText);
    for (let tentativa = 0; tentativa < 3 && !aberto(); tentativa++) {
      esc(); await esperar(250);
      t.click(); await esperar(700);
      if (pop() && T.avisoCredito.test(pop().innerText)) {   // sem crédito, abre um aviso antes dos ajustes
        const s = botoes(pop()).find(b => T.botaoAjustesDoAviso.test(rot(b)));
        if (s) { s.click(); await esperar(700); }
      }
    }
    if (!aberto()) throw new Error('não consegui abrir o painel de ajustes');
    return pop();
  }

  const lerAjustes = () => (acha(T.ajustes) || { textContent: '' }).textContent.trim().replace(/\s+/g, ' ');

  async function custo() {
    const p = await abrirAjustes();
    const m = p.innerText.match(T.custo);
    esc(); await esperar(200);
    return m ? Number(m[1]) : null;
  }

  async function configurar(o = {}) {
    const p = await abrirAjustes();
    for (const v of [o.tipo, o.modo, o.proporcao, o.res, o.dur, o.qtd].filter(Boolean)) {
      const b = termina(v, p);
      if (!b) { esc(); throw new Error('opção não encontrada: ' + v); }
      b.click(); await esperar(300);
    }
    const r = { ajustes: lerAjustes(), custo: Number((p.innerText.match(T.custo) || [])[1]) || null };
    esc(); await esperar(200);
    return r;
  }

  const semCredito = () => !!acha(T.semCredito);

  async function estado() {
    return { ajustes: lerAjustes(), custo: await custo(), semCredito: semCredito(),
             prompt: (document.querySelector('.ProseMirror') || {}).innerText || '', tiles: listar().length };
  }

  async function preencher(texto) {
    const ed = document.querySelector('.ProseMirror');
    if (!ed) throw new Error('campo do prompt não encontrado');
    ed.focus();
    document.execCommand('selectAll');
    document.execCommand('insertText', false, texto);
    await esperar(300);
    return ed.innerText.trim() === texto.trim() ? 'ok' : 'conferir: o texto no campo ficou diferente';
  }

  async function limpar() {   // apaga o prompt e as imagens de referência da caixa
    const b = acha(T.limpar);
    if (b) { b.click(); await esperar(400); }
    return (document.querySelector('.ProseMirror') || {}).innerText.trim() === '' ? 'ok' : 'conferir';
  }

  async function menuDoTile(tile, icone) {   // icone: nome do ícone do item ('add_2', 'download'), igual em todo idioma
    const mais = botoes(tile).find(b => T.mais.test(rot(b)));
    if (!mais) throw new Error('menu do tile não encontrado');
    mais.click(); await esperar(600);
    const it = itensMenu().find(b => b.textContent.trim().startsWith(icone));
    if (!it) { esc(); throw new Error('item de menu não encontrado: ' + icone); }
    it.click(); await esperar(700);
  }

  const tilesEls = () => [...document.querySelectorAll('flow-grid-tile-container')];

  function listar() {
    return tilesEls().map((t, i) => {
      const titulo = botoes(t).map(rot).find(x => x && !T.titulo.test(x)) || '';
      const txt = t.innerText;
      return { i, tipo: t.querySelector('flow-video-tile') ? 'video' : 'imagem', titulo: titulo.slice(0, 60),
               progresso: (txt.match(/\d+%/) || [''])[0], erro: /error|failed|falhou|erro/i.test(txt) };
    });
  }

  async function ingrediente(titulo) {
    const t = tilesEls().find(el => botoes(el).some(b => rot(b).includes(titulo)));
    if (!t) throw new Error('tile não encontrado: ' + titulo);
    await menuDoTile(t, 'add_2');
    return 'ok';
  }

  async function gerar({ limite } = {}) {
    if (limite == null) throw new Error('passe o limite de créditos aprovado: gerar({limite: N})');
    const c = await custo();
    if (semCredito()) return { gerou: false, motivo: 'sem crédito no Flow' };
    if (c == null || c > limite) return { gerou: false, motivo: `custo ${c} acima do limite ${limite}` };
    const go = acha(T.gerar);
    if (!go || go.disabled) return { gerou: false, motivo: 'botão de gerar desabilitado (prompt vazio?)' };
    const antes = listar().length;
    go.click(); await esperar(2500);
    return { gerou: true, custo: c, tilesAntes: antes, tilesDepois: listar().length };
  }

  async function baixar(i, qualidade = '720p') {
    if (!['720p', '270p'].includes(qualidade)) throw new Error('só 720p (original) ou 270p (GIF): upscale gasta crédito e precisa do "sim"');
    const t = tilesEls()[i];
    if (!t) throw new Error('tile não existe: ' + i);
    await menuDoTile(t, 'download');
    const q = itensMenu().find(b => rot(b).startsWith(qualidade));
    if (!q) { esc(); throw new Error('qualidade não encontrada: ' + qualidade); }
    q.click(); await esperar(1500);
    return 'pedido de download enviado (confira a pasta de downloads)';
  }

  window.flowLote = { estado, configurar, custo, preencher, limpar, ingrediente, gerar, listar, baixar, semCredito };
  return 'flowLote pronto: ' + Object.keys(window.flowLote).join(', ');
})();
