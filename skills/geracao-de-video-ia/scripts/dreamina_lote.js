// Modo lote do Dreamina (dreamina.capcut.com, Seedance), rodando na aba já logada pelo Claude in Chrome.
// Mapeado em 2026-11-18 na interface em português (Criar > Vídeo de IA > modelo). Injete o arquivo inteiro uma
// vez por aba (javascript_tool) na página de geração (ai-tool/generate ... ai_feature_name=video).
//   await dreaminaLote.estado()          -> modelo, modo de referência, proporção, resolução, duração, custo, saldo
//   await dreaminaLote.configurar({modelo:'Seedance 2.0 Mini', referencia:'Referência universal',
//                                  proporcao:'9:16', res:'720P', dur:8})   -> devolve o custo da próxima geração
//   await dreaminaLote.preencher('prompt')     -> escreve o prompt (substitui o anterior)
//   (a imagem de referência entra pelo file_upload do Claude in Chrome no <input type=file> da caixa,
//    ou arrastando um ativo já enviado; confira com estado().refs)
//   await dreaminaLote.gerar({limite: 300})    -> só envia se custo <= limite (o limite vem do "sim" do usuário)
//   dreaminaLote.listar()                      -> gerações da página: prompt, progresso, src do vídeo
//   await dreaminaLote.baixar(i)               -> baixa o vídeo i por fetch + <a download> (1 download por aba)
// Nenhuma função aprova gasto sozinha.
(() => {
  const esperar = ms => new Promise(r => setTimeout(r, ms));
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const txt = e => (e.innerText || e.textContent || '').trim().replace(/\s+/g, ' ');
  const fechar = async () => { document.body.click(); document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); await esperar(300); };
  const botoesBarra = () => [...document.querySelectorAll('button,[role=combobox]')].filter(vis);
  const pop = () => [...document.querySelectorAll('.lv-popover-inner,.lv-select-popup,.lv-trigger-popup')].filter(vis).pop();
  const editor = () => [...document.querySelectorAll('.tiptap.ProseMirror')].filter(vis)[0];
  const enviar = () => [...document.querySelectorAll('button.lv-btn-primary.lv-btn-shape-circle')].filter(vis).pop();

  function custo() {   // número ao lado do botão de enviar (o riscado é o preço sem desconto)
    const b = enviar(); if (!b) return null;
    let p = b.parentElement;
    for (let i = 0; i < 3 && p && !/\d/.test(txt(p)); i++) p = p.parentElement;
    const m = p && txt(p).match(/(\d[\d.]*)/);
    return m ? Number(m[1].replace(/\./g, '')) : null;
  }
  function saldo() {   // canto superior direito (ex.: "5.2K"); o cronômetro da promoção também tem números
    const e = [...document.querySelectorAll('*')].filter(vis).filter(x => x.childElementCount === 0 && /^\d+(\.\d+)?K$|^\d{2,6}$/.test(txt(x)))
      .filter(x => { const r = x.getBoundingClientRect(); return r.top < 90 && r.left > window.innerWidth * 0.75; }).pop();
    return e ? txt(e) : null;
  }
  async function escolherRadio(abridor, rotulo) {   // proporção e resolução ficam no mesmo popover
    // os popovers do Dreamina não fecham com Esc e ficam vários abertos: procura o rótulo em todos
    if (![...document.querySelectorAll('label.lv-radio')].some(x => vis(x) && txt(x) === rotulo)) { abridor.click(); await esperar(600); }
    const l = [...document.querySelectorAll('label.lv-radio')].filter(vis).find(x => txt(x) === rotulo);
    if (!l) { await fechar(); throw new Error('opção não encontrada: ' + rotulo); }
    l.click(); await esperar(400);
  }
  async function escolherMenu(abridor, comeco) {
    abridor.click(); await esperar(700);
    const itens = [...document.querySelectorAll('[role=option],li,[class*=menu-item],[class*=option]')].filter(vis);
    const it = itens.find(x => txt(x).startsWith(comeco));
    if (!it) { await fechar(); throw new Error('item não encontrado: ' + comeco); }
    it.click(); await esperar(600);
  }
  const bModelo = () => botoesBarra().find(b => /Seedance|Wan/.test(txt(b)) && b.getAttribute('role') === 'combobox');
  const naCaixa = b => !b.className.toString().includes('navigation-item') && b.getBoundingClientRect().left > 250;   // fora da barra lateral
  const bRef = () => botoesBarra().filter(naCaixa).find(b => /^(Referência universal|Primeiro e último|Vários quadros|Edição inteligente|Vídeo longo|Recriador)/.test(txt(b)));
  const bProp = () => botoesBarra().find(b => /^\d+:\d+ \d+[PK]/.test(txt(b)));
  const bDur = () => botoesBarra().find(b => /^\d+s$/.test(txt(b)));

  async function duracao(seg) {
    bDur().click(); await esperar(600);
    const i = [...document.querySelectorAll('input[role=spinbutton]')].filter(vis)[0];
    if (!i) throw new Error('campo de duração não encontrado');
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    i.focus(); set.call(i, String(seg)); i.dispatchEvent(new Event('input', { bubbles: true }));
    i.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); i.blur();
    await esperar(400); await fechar();
  }

  async function estado() {
    await fechar();
    return { modelo: bModelo() && txt(bModelo()), referencia: bRef() && txt(bRef()), proporcao: bProp() && txt(bProp()),
             duracao: bDur() && txt(bDur()), custo: custo(), saldo: saldo(), prompt: editor() ? txt(editor()) : null,
             refs: [...document.querySelectorAll('img')].filter(vis).filter(im => im.closest('[class*=reference],[class*=upload]')).length };
  }

  async function configurar(o = {}) {
    await fechar();
    if (o.modelo && !txt(bModelo()).includes(o.modelo)) await escolherMenu(bModelo(), 'Dreamina ' + o.modelo.replace(/^Dreamina /, ''));
    if (o.referencia && !txt(bRef()).startsWith(o.referencia)) await escolherMenu(bRef(), o.referencia);
    if (o.proporcao) { await escolherRadio(bProp(), o.proporcao); await fechar(); }
    if (o.res) { await escolherRadio(bProp(), o.res); await fechar(); }
    if (o.dur) await duracao(o.dur);
    await esperar(500);
    return estado();
  }

  async function preencher(texto) {
    const ed = editor(); if (!ed) throw new Error('campo do prompt não encontrado');
    ed.focus(); document.execCommand('selectAll'); document.execCommand('delete');
    document.execCommand('insertText', false, texto); await esperar(400);
    return txt(ed) === texto.trim().replace(/\s+/g, ' ') ? 'ok' : 'conferir: o texto no campo ficou diferente';
  }

  async function gerar({ limite } = {}) {
    if (limite == null) throw new Error('passe o limite de créditos aprovado: gerar({limite: N})');
    const c = custo();
    if (c == null || c > limite) return { gerou: false, motivo: `custo ${c} acima do limite ${limite}` };
    const b = enviar(); if (!b || b.disabled) return { gerou: false, motivo: 'botão de enviar desabilitado (prompt ou referência faltando?)' };
    const antes = listar().length; b.click(); await esperar(3000);
    return { gerou: true, custo: c, antes, depois: listar().length };
  }

  function listar() {   // cada geração: o vídeo e o prompt que vem antes dele na página
    return [...document.querySelectorAll('video')].filter(v => v.src || v.querySelector('source')).map((v, i) => {
      let p = v; for (let k = 0; k < 8 && p && !/\w{20}/.test(txt(p)); k++) p = p.parentElement;
      return { i, src: (v.currentSrc || v.src || '').slice(0, 80), prompt: p ? txt(p).slice(0, 80) : '', progresso: '' };
    });
  }

  async function baixar(i, nome) {
    const v = [...document.querySelectorAll('video')].filter(x => x.src || x.querySelector('source'))[i];
    if (!v) throw new Error('vídeo não existe: ' + i);
    const blob = await (await fetch(v.currentSrc || v.src)).blob();
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = nome || `dreamina_${i}.mp4`;
    document.body.appendChild(a); a.click(); a.remove();
    return `pedido de download: ${a.download} (${Math.round(blob.size / 1024)} KB)`;
  }

  window.dreaminaLote = { estado, configurar, custo, saldo, preencher, gerar, listar, baixar };
  return 'dreaminaLote pronto: ' + Object.keys(window.dreaminaLote).join(', ');
})();
