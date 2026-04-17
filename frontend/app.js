/* ═══════════════════════════════════════════════════════════════════════════
   Mercado Público de Solânea – Sistema de Gestão
   Frontend SPA – Vanilla JS
══════════════════════════════════════════════════════════════════════════════ */

'use strict';

// ── Config ───────────────────────────────────────────────────────────────────
const API = '/api';
const PER_PAGE = 10;

// ── State ────────────────────────────────────────────────────────────────────
let token = null;
let currentUser = null;
let allCessionarios = [];
let allPagamentos = [];
let cessPagina = 1;
let pagPagina = 1;

// ── API helper ───────────────────────────────────────────────────────────────
async function api(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const opts = { method, headers };
  if (body !== null) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const msg = data?.detail || `Erro ${res.status}`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
  return data;
}

// ── Utilities ────────────────────────────────────────────────────────────────
function fR(n) {
  return 'R$ ' + Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fD(s) {
  if (!s) return '–';
  const d = new Date(s + (s.length === 10 ? 'T00:00:00' : ''));
  return d.toLocaleDateString('pt-BR');
}
function fDT(s) {
  if (!s) return '–';
  const d = new Date(s);
  return d.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
}
function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function today() {
  return new Date().toISOString().slice(0, 10);
}

// ── Toast ────────────────────────────────────────────────────────────────────
function toast(msg, type = 'ok') {
  const container = document.getElementById('toast-container');
  const icons = { ok: '✅', err: '❌', warn: '⚠️', info: 'ℹ️' };
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.innerHTML = `<span>${icons[type] || '💬'}</span> <span>${esc(msg)}</span>`;
  container.appendChild(el);
  setTimeout(() => {
    el.classList.add('out');
    el.addEventListener('animationend', () => el.remove());
  }, 4000);
}

// ── Modals ────────────────────────────────────────────────────────────────────
function openModal(id) {
  document.getElementById(id).classList.add('open');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}
// Close on backdrop click
document.querySelectorAll('.modal-backdrop').forEach(bd => {
  bd.addEventListener('click', e => {
    if (e.target === bd) bd.classList.remove('open');
  });
});

// ── Sidebar ───────────────────────────────────────────────────────────────────
function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  const ov = document.getElementById('sidebar-overlay');
  sb.classList.toggle('open');
  ov.classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('open');
}

// ── Navigation ────────────────────────────────────────────────────────────────
const pageTitles = {
  dashboard: 'Dashboard',
  cessionarios: 'Cessionários',
  pagamentos: 'Pagamentos',
  relatorios: 'Relatórios',
  usuarios: 'Usuários',
};

function showTab(tab) {
  ['dashboard', 'cessionarios', 'pagamentos', 'relatorios', 'usuarios'].forEach(t => {
    const el = document.getElementById('t-' + t);
    if (el) el.classList.toggle('hidden', t !== tab);
  });
  document.querySelectorAll('.nav-item').forEach(n => {
    n.classList.toggle('active', n.dataset.tab === tab);
  });
  document.getElementById('page-title').textContent = pageTitles[tab] || tab;
  closeSidebar();

  if (tab === 'dashboard') loadDashboard();
  else if (tab === 'cessionarios') loadCessionarios();
  else if (tab === 'pagamentos') loadPagamentos();
  else if (tab === 'usuarios') loadUsuarios();
  else if (tab === 'relatorios') initRelatorios();
}

document.getElementById('sidebar-nav').addEventListener('click', e => {
  const item = e.target.closest('.nav-item');
  if (item && item.dataset.tab) showTab(item.dataset.tab);
});

// ── Auth ──────────────────────────────────────────────────────────────────────
function showSection(id) {
  ['s-login', 's-pending', 's-app'].forEach(s => {
    const el = document.getElementById(s);
    el.classList.toggle('hidden', s !== id);
  });
}

async function doLogin() {
  const email = document.getElementById('l-email').value.trim();
  const senha = document.getElementById('l-senha').value;
  const errEl = document.getElementById('login-error');
  const btn = document.getElementById('btn-login');

  errEl.style.display = 'none';
  if (!email || !senha) {
    errEl.textContent = 'Preencha e-mail e senha.';
    errEl.style.display = 'block';
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Entrando…';
  try {
    const data = await api('POST', '/auth/login', { email, senha });
    applyLogin(data);
  } catch (e) {
    errEl.textContent = e.message;
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>🔑</span> Entrar';
  }
}

function applyLogin(data) {
  token = data.access_token;
  currentUser = {
    id: data.user_id,
    nome: data.nome,
    is_admin: data.is_admin,
    aprovado: data.aprovado,
  };
  sessionStorage.setItem('mp_token', token);
  sessionStorage.setItem('mp_user', JSON.stringify(currentUser));

  if (!data.aprovado) {
    showSection('s-pending');
    return;
  }
  enterApp();
}

function enterApp() {
  showSection('s-app');
  // Update sidebar user info
  document.getElementById('user-name').textContent = currentUser.nome;
  document.getElementById('user-role').textContent = currentUser.is_admin ? 'Administrador' : 'Operador';
  document.getElementById('user-avatar').textContent = currentUser.nome.charAt(0).toUpperCase();
  if (currentUser.is_admin) {
    document.getElementById('nav-usuarios').classList.remove('hidden');
    document.getElementById('th-cadastrador').classList.remove('hidden');
  }
  showTab('dashboard');
}

function logout() {
  token = null;
  currentUser = null;
  sessionStorage.removeItem('mp_token');
  sessionStorage.removeItem('mp_user');
  showSection('s-login');
}

// ── Login form events ─────────────────────────────────────────────────────────
document.getElementById('btn-login').addEventListener('click', doLogin);
document.getElementById('l-senha').addEventListener('keydown', e => {
  if (e.key === 'Enter') doLogin();
});
document.getElementById('l-email').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('l-senha').focus();
});

// ── Dashboard ─────────────────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const stats = await api('GET', '/relatorios/dashboard');
    document.getElementById('k-total').textContent = stats.total_cess;
    document.getElementById('k-reg').textContent = stats.regulares;
    document.getElementById('k-irr').textContent = stats.irregulares;
    document.getElementById('k-arr').textContent = fR(stats.total_arrecadado);
    document.getElementById('k-mes').textContent = fR(stats.pagamentos_mensais);
    document.getElementById('k-npag').textContent = stats.total_pagamentos;

    renderDonut(stats.regulares, stats.irregulares);
    renderBarChart(stats.grafico_6meses);
    renderTopPagadores(stats.top_pagadores);
    renderAtividade(stats.atividade_recente);
  } catch (e) {
    toast('Erro ao carregar dashboard: ' + e.message, 'err');
  }
}

function renderDonut(regulares, irregulares) {
  const total = regulares + irregulares || 1;
  const percR = regulares / total;
  const percI = irregulares / total;
  const r = 60;
  const cx = 70, cy = 70;
  const circum = 2 * Math.PI * r;

  function arc(perc, color, offset) {
    return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${color}"
      stroke-width="18" stroke-dasharray="${(perc * circum).toFixed(1)} ${circum.toFixed(1)}"
      stroke-dashoffset="${(-offset * circum).toFixed(1)}"
      transform="rotate(-90 ${cx} ${cy})" stroke-linecap="butt"/>`;
  }

  const svg = `
    <svg width="140" height="140" viewBox="0 0 140 140">
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#e2e8f0" stroke-width="18"/>
      ${arc(percR, '#16a34a', 0)}
      ${arc(percI, '#dc2626', percR)}
      <text x="${cx}" y="${cy - 6}" text-anchor="middle" font-size="18" font-weight="800" fill="#0f172a">${total}</text>
      <text x="${cx}" y="${cy + 14}" text-anchor="middle" font-size="9" fill="#64748b">TOTAL</text>
    </svg>`;

  document.getElementById('donut-wrap').innerHTML = `
    ${svg}
    <div class="donut-legend">
      <div class="legend-item">
        <div class="legend-dot" style="background:#16a34a"></div>
        <span>Regulares: <strong>${regulares}</strong></span>
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#dc2626"></div>
        <span>Irregulares: <strong>${irregulares}</strong></span>
      </div>
    </div>`;
}

function renderBarChart(data) {
  if (!data || !data.length) {
    document.getElementById('bar-wrap').innerHTML = '<div class="empty-state"><div class="empty-icon">📊</div><p>Sem dados</p></div>';
    return;
  }
  const maxVal = Math.max(...data.map(d => d.total), 1);
  const W = 380, H = 160, pad = 40, barW = 36, gap = (W - pad * 2 - data.length * barW) / (data.length - 1 || 1);
  let bars = '', labels = '', values = '';
  data.forEach((d, i) => {
    const x = pad + i * (barW + gap);
    const barH = Math.max(4, (d.total / maxVal) * (H - 50));
    const y = H - 30 - barH;
    bars += `<rect x="${x}" y="${y}" width="${barW}" height="${barH}" rx="4" fill="#2563eb" opacity="${d.total > 0 ? 1 : 0.3}"/>`;
    labels += `<text x="${x + barW / 2}" y="${H - 8}" text-anchor="middle" font-size="10" fill="#64748b">${esc(d.mes)}</text>`;
    if (d.total > 0) {
      values += `<text x="${x + barW / 2}" y="${y - 5}" text-anchor="middle" font-size="9" fill="#1e3a5f" font-weight="600">
        ${d.total >= 1000 ? (d.total / 1000).toFixed(1) + 'k' : d.total.toFixed(0)}</text>`;
    }
  });
  document.getElementById('bar-wrap').innerHTML =
    `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto">${bars}${labels}${values}</svg>`;
}

function renderTopPagadores(top) {
  const el = document.getElementById('top-pagadores');
  if (!top || !top.length) {
    el.innerHTML = '<div class="empty-state"><p>Sem dados</p></div>';
    return;
  }
  el.innerHTML = top.map((t, i) => `
    <div class="top-item">
      <div class="top-rank">${i + 1}</div>
      <div class="top-name">${esc(t.nome)}</div>
      <div class="top-val">${fR(t.total)}</div>
    </div>`).join('');
}

function renderAtividade(atividade) {
  const el = document.getElementById('activity-list');
  if (!atividade || !atividade.length) {
    el.innerHTML = '<div class="empty-state" style="padding:1.5rem"><p>Nenhuma atividade recente</p></div>';
    return;
  }
  el.innerHTML = atividade.map(a => `
    <div class="activity-item">
      <div class="activity-dot"></div>
      <div class="activity-text">${esc(a.descricao)}${a.usuario ? ` <span class="text-muted">– ${esc(a.usuario)}</span>` : ''}</div>
      <div class="activity-meta">${fDT(a.data)}</div>
    </div>`).join('');
}

// ── Cessionários ──────────────────────────────────────────────────────────────
async function loadCessionarios() {
  try {
    allCessionarios = await api('GET', '/cessionarios');
    cessPagina = 1;
    renderCessionarios();
  } catch (e) {
    toast('Erro ao carregar cessionários: ' + e.message, 'err');
  }
}

function filterCessionarios() {
  cessPagina = 1;
  renderCessionarios();
}

function getCessFiltered() {
  const nome = (document.getElementById('f-cess-nome').value || '').toLowerCase();
  const sit = document.getElementById('f-cess-sit').value;
  const per = document.getElementById('f-cess-per').value;
  return allCessionarios.filter(c => {
    const matchNome = !nome || c.nome.toLowerCase().includes(nome);
    const matchSit = !sit || c.situacao === sit;
    const matchPer = !per || c.per_ref === per;
    return matchNome && matchSit && matchPer;
  });
}

function renderCessionarios() {
  const filtered = getCessFiltered();
  const total = filtered.length;
  const pages = Math.ceil(total / PER_PAGE) || 1;
  cessPagina = Math.min(cessPagina, pages);
  const slice = filtered.slice((cessPagina - 1) * PER_PAGE, cessPagina * PER_PAGE);
  const tbody = document.getElementById('tb-cessionarios');

  if (!slice.length) {
    tbody.innerHTML = `<tr><td colspan="10" class="empty-state"><div class="empty-icon">🏪</div><p>Nenhum cessionário encontrado</p></td></tr>`;
    document.getElementById('pag-cessionarios').innerHTML = '';
    return;
  }

  tbody.innerHTML = slice.map(c => {
    const badge = c.situacao === 'Regular'
      ? '<span class="badge badge-success">● Regular</span>'
      : '<span class="badge badge-danger">● Irregular</span>';
    const tel = c.telefone
      ? `<a href="https://wa.me/55${c.telefone.replace(/\D/g, '')}" target="_blank" title="WhatsApp" style="color:var(--success)">📱 ${esc(c.telefone)}</a>`
      : '–';
    const adm = currentUser.is_admin ? `<td>${esc(c.cadastrador_nome || '–')}</td>` : '';
    return `<tr>
      <td>${esc(c.numero_box || '–')}</td>
      <td><strong>${esc(c.nome)}</strong></td>
      <td>${esc(c.atividade || '–')}</td>
      <td>${tel}</td>
      <td>${badge}</td>
      <td>${fR(c.valor_ref)}</td>
      <td>${fR(c.total_pago)}</td>
      <td>${fD(c.ultimo_pagamento)}</td>
      ${adm}
      <td class="col-actions">
        <button class="btn btn-ghost btn-sm" onclick="openCessModal('${c.id}')" title="Editar">✏️</button>
        <button class="btn btn-ghost btn-sm" onclick="emitirCertidao('${c.id}')" title="Certidão">📜</button>
        <button class="btn btn-ghost btn-sm" onclick="confirmDelete('cess','${c.id}','${esc(c.nome)}')" title="Excluir" style="color:var(--danger)">🗑️</button>
      </td>
    </tr>`;
  }).join('');

  renderPagination(document.getElementById('pag-cessionarios'), total, cessPagina, PER_PAGE, p => {
    cessPagina = p;
    renderCessionarios();
  });
}

function openCessModal(id = null) {
  const isEdit = !!id;
  document.getElementById('m-cess-title').textContent = isEdit ? 'Editar Cessionário' : 'Novo Cessionário';
  document.getElementById('mc-id').value = '';
  document.getElementById('mc-nome').value = '';
  document.getElementById('mc-box').value = '';
  document.getElementById('mc-ativ').value = '';
  document.getElementById('mc-tel').value = '';
  document.getElementById('mc-sit').value = 'Regular';
  document.getElementById('mc-per').value = 'Mensal';
  document.getElementById('mc-val').value = '';
  document.getElementById('mc-obs').value = '';

  if (isEdit) {
    const c = allCessionarios.find(x => x.id === id);
    if (!c) return;
    document.getElementById('mc-id').value = c.id;
    document.getElementById('mc-nome').value = c.nome;
    document.getElementById('mc-box').value = c.numero_box || '';
    document.getElementById('mc-ativ').value = c.atividade || '';
    document.getElementById('mc-tel').value = c.telefone || '';
    document.getElementById('mc-sit').value = c.situacao;
    document.getElementById('mc-per').value = c.per_ref;
    document.getElementById('mc-val').value = c.valor_ref;
    document.getElementById('mc-obs').value = c.observacao || '';
  }
  openModal('m-cess');
}

async function saveCessionario() {
  const id = document.getElementById('mc-id').value;
  const nome = document.getElementById('mc-nome').value.trim();
  if (!nome) { toast('Nome é obrigatório', 'warn'); return; }
  const body = {
    nome,
    numero_box: document.getElementById('mc-box').value.trim() || null,
    atividade: document.getElementById('mc-ativ').value.trim() || null,
    telefone: document.getElementById('mc-tel').value.trim() || null,
    situacao: document.getElementById('mc-sit').value,
    per_ref: document.getElementById('mc-per').value,
    valor_ref: parseFloat(document.getElementById('mc-val').value) || 0,
    observacao: document.getElementById('mc-obs').value.trim() || null,
  };
  const btn = document.getElementById('btn-save-cess');
  btn.disabled = true;
  try {
    if (id) {
      await api('PATCH', `/cessionarios/${id}`, body);
      toast('Cessionário atualizado!');
    } else {
      await api('POST', '/cessionarios', body);
      toast('Cessionário criado!');
    }
    closeModal('m-cess');
    await loadCessionarios();
  } catch (e) {
    toast(e.message, 'err');
  } finally {
    btn.disabled = false;
  }
}

async function deleteCessionario(id) {
  try {
    await api('DELETE', `/cessionarios/${id}`);
    toast('Cessionário excluído!');
    await loadCessionarios();
  } catch (e) {
    toast(e.message, 'err');
  }
}

// ── Certidão ──────────────────────────────────────────────────────────────────
async function emitirCertidao(id) {
  try {
    const cert = await api('GET', `/cessionarios/${id}/certidao`);
    const aus = cert.ausencias;
    const sitBadge = cert.situacao === 'Regular'
      ? '<span class="badge badge-success">● Regular</span>'
      : '<span class="badge badge-danger">● Irregular</span>';
    const ausHtml = aus.length
      ? `<div class="certidao-ausencias">⚠️ ${aus.length} período(s) sem pagamento: ${aus.slice(0, 15).map(esc).join(', ')}${aus.length > 15 ? `... (+${aus.length - 15} mais)` : ''}</div>`
      : '<div class="certidao-ok">✅ Nenhum período sem pagamento detectado.</div>';

    document.getElementById('certidao-content').innerHTML = `
      <div class="certidao-preview">
        <div class="certidao-title">
          <h3>Certidão de Situação Cadastral</h3>
          <p>Prefeitura Municipal de Solânea – PB | Mercado Público Municipal</p>
          <p style="font-size:.75rem;color:var(--text-muted)">Nº ${esc(cert.numero)}</p>
        </div>
        <div class="certidao-row"><span class="cl">Cessionário:</span><span class="cv">${esc(cert.cessionario)}</span></div>
        <div class="certidao-row"><span class="cl">Box:</span><span class="cv">${esc(cert.numero_box || '–')}</span></div>
        <div class="certidao-row"><span class="cl">Atividade:</span><span class="cv">${esc(cert.atividade || '–')}</span></div>
        <div class="certidao-row"><span class="cl">Situação:</span><span class="cv">${sitBadge}</span></div>
        <div class="certidao-row"><span class="cl">Periodicidade:</span><span class="cv">${esc(cert.periodicidade)}</span></div>
        <div class="certidao-row"><span class="cl">Último Pag.:</span><span class="cv">${fD(cert.ultimo_pagamento)}</span></div>
        <div class="certidao-row"><span class="cl">Total Pago:</span><span class="cv">${fR(cert.total_pago)}</span></div>
        <div class="certidao-row"><span class="cl">Valor Ref.:</span><span class="cv">${fR(cert.valor_ref)}</span></div>
        <div class="certidao-row"><span class="cl">Emitido por:</span><span class="cv">${esc(cert.emitido_por)}</span></div>
        <div class="certidao-row"><span class="cl">Emitido em:</span><span class="cv">${fDT(cert.emitido_em)}</span></div>
        ${ausHtml}
      </div>`;

    document.getElementById('btn-cert-pdf').onclick = () => downloadCertidaoPDF(id);
    openModal('m-certidao');
  } catch (e) {
    toast(e.message, 'err');
  }
}

function downloadCertidaoPDF(id) {
  const url = `${API}/relatorios/cessionarios/${id}/certidao/pdf`;
  const a = document.createElement('a');
  a.href = url;
  a.setAttribute('download', '');
  // Need token in header – use fetch blob
  fetchDownload(url, `certidao_${id}.pdf`);
}

// ── Pagamentos ────────────────────────────────────────────────────────────────
async function loadPagamentos() {
  try {
    allPagamentos = await api('GET', '/pagamentos');
    pagPagina = 1;
    renderPagamentos();
  } catch (e) {
    toast('Erro ao carregar pagamentos: ' + e.message, 'err');
  }
}

function filterPagamentos() {
  pagPagina = 1;
  renderPagamentos();
}

function getPagFiltered() {
  const nome = (document.getElementById('f-pag-nome').value || '').toLowerCase();
  const per = document.getElementById('f-pag-per').value;
  const di = document.getElementById('f-pag-di').value;
  const df = document.getElementById('f-pag-df').value;
  return allPagamentos.filter(p => {
    const matchNome = !nome || (p.cessionario_nome || '').toLowerCase().includes(nome);
    const matchPer = !per || p.periodicidade === per;
    const matchDi = !di || p.data >= di;
    const matchDf = !df || p.data <= df;
    return matchNome && matchPer && matchDi && matchDf;
  });
}

function renderPagamentos() {
  const filtered = getPagFiltered();
  const total = filtered.length;
  const pages = Math.ceil(total / PER_PAGE) || 1;
  pagPagina = Math.min(pagPagina, pages);
  const slice = filtered.slice((pagPagina - 1) * PER_PAGE, pagPagina * PER_PAGE);
  const tbody = document.getElementById('tb-pagamentos');

  if (!slice.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="empty-state"><div class="empty-icon">💳</div><p>Nenhum pagamento encontrado</p></td></tr>`;
    document.getElementById('pag-pagamentos').innerHTML = '';
    return;
  }

  tbody.innerHTML = slice.map(p => {
    const adminActions = currentUser.is_admin
      ? `<button class="btn btn-ghost btn-sm" onclick="openPagModal('${p.id}')" title="Editar">✏️</button>
         <button class="btn btn-ghost btn-sm" onclick="confirmDelete('pag','${p.id}','pagamento de ${fR(p.valor)}')" title="Excluir" style="color:var(--danger)">🗑️</button>`
      : '';
    return `<tr>
      <td>${fD(p.data)}</td>
      <td><strong>${esc(p.cessionario_nome || '–')}</strong></td>
      <td>${esc(p.cessionario_box || '–')}</td>
      <td><span class="badge badge-info">${esc(p.periodicidade)}</span></td>
      <td><strong class="text-success">${fR(p.valor)}</strong></td>
      <td>${esc(p.usuario_nome || '–')}</td>
      <td style="max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${esc(p.observacao || '–')}</td>
      <td class="col-actions">${adminActions}</td>
    </tr>`;
  }).join('');

  renderPagination(document.getElementById('pag-pagamentos'), total, pagPagina, PER_PAGE, p => {
    pagPagina = p;
    renderPagamentos();
  });
}

async function openPagModal(id = null) {
  // Populate cessionário select
  if (!allCessionarios.length) {
    try { allCessionarios = await api('GET', '/cessionarios'); } catch {}
  }
  const sel = document.getElementById('mp-cess');
  sel.innerHTML = '<option value="">Selecione...</option>' +
    allCessionarios.map(c => `<option value="${c.id}">${esc(c.nome)} (${esc(c.numero_box || 'S/Box')})</option>`).join('');

  document.getElementById('m-pag-title').textContent = id ? 'Editar Pagamento' : 'Novo Pagamento';
  document.getElementById('mp-id').value = '';
  document.getElementById('mp-cess').value = '';
  document.getElementById('mp-data').value = today();
  document.getElementById('mp-per').value = 'Mensal';
  document.getElementById('mp-val').value = '';
  document.getElementById('mp-obs').value = '';
  document.getElementById('mp-hint').classList.remove('visible');

  if (id) {
    const p = allPagamentos.find(x => x.id === id);
    if (p) {
      document.getElementById('mp-id').value = p.id;
      document.getElementById('mp-cess').value = p.cessionario_id;
      document.getElementById('mp-data').value = p.data;
      document.getElementById('mp-per').value = p.periodicidade;
      document.getElementById('mp-val').value = p.valor;
      document.getElementById('mp-obs').value = p.observacao || '';
      onCessSelectChange();
    }
  }
  openModal('m-pag');
}

function onCessSelectChange() {
  const cessId = document.getElementById('mp-cess').value;
  const cess = allCessionarios.find(c => c.id === cessId);
  const hintEl = document.getElementById('mp-hint');
  const hintVal = document.getElementById('mp-hint-val');
  if (cess && cess.valor_ref > 0) {
    hintEl.classList.add('visible');
    hintVal.textContent = fR(cess.valor_ref);
    // Also set periodicidade from cess
    document.getElementById('mp-per').value = cess.per_ref || 'Mensal';
  } else {
    hintEl.classList.remove('visible');
  }
}

function useHintValue() {
  const cessId = document.getElementById('mp-cess').value;
  const cess = allCessionarios.find(c => c.id === cessId);
  if (cess) document.getElementById('mp-val').value = cess.valor_ref;
}

async function savePagamento() {
  const id = document.getElementById('mp-id').value;
  const cessionario_id = document.getElementById('mp-cess').value;
  const data_val = document.getElementById('mp-data').value;
  const valor = parseFloat(document.getElementById('mp-val').value);

  if (!cessionario_id) { toast('Selecione um cessionário', 'warn'); return; }
  if (!data_val) { toast('Informe a data', 'warn'); return; }
  if (!valor || valor <= 0) { toast('Valor deve ser maior que zero', 'warn'); return; }

  const body = {
    cessionario_id,
    data: data_val,
    valor,
    periodicidade: document.getElementById('mp-per').value,
    observacao: document.getElementById('mp-obs').value.trim() || null,
  };

  const btn = document.getElementById('btn-save-pag');
  btn.disabled = true;
  try {
    if (id) {
      await api('PATCH', `/pagamentos/${id}`, body);
      toast('Pagamento atualizado!');
    } else {
      await api('POST', '/pagamentos', body);
      toast('Pagamento registrado!');
    }
    closeModal('m-pag');
    await loadPagamentos();
  } catch (e) {
    toast(e.message, 'err');
  } finally {
    btn.disabled = false;
  }
}

async function deletePagamento(id) {
  try {
    await api('DELETE', `/pagamentos/${id}`);
    toast('Pagamento excluído!');
    await loadPagamentos();
  } catch (e) {
    toast(e.message, 'err');
  }
}

// ── Confirm delete ────────────────────────────────────────────────────────────
function confirmDelete(tipo, id, nome) {
  document.getElementById('m-confirm-title').textContent = 'Confirmar Exclusão';
  document.getElementById('m-confirm-text').textContent =
    `Tem certeza que deseja excluir "${nome}"?` +
    (tipo === 'cess' ? ' Todos os pagamentos associados também serão excluídos.' : '');
  document.getElementById('btn-confirm-ok').onclick = () => {
    closeModal('m-confirm');
    if (tipo === 'cess') deleteCessionario(id);
    else if (tipo === 'pag') deletePagamento(id);
    else if (tipo === 'user') deleteUsuario(id);
  };
  openModal('m-confirm');
}

// ── Usuários ──────────────────────────────────────────────────────────────────
let allUsuarios = [];

async function loadUsuarios() {
  try {
    allUsuarios = await api('GET', '/users');
    renderUsuarios();
  } catch (e) {
    toast('Erro ao carregar usuários: ' + e.message, 'err');
  }
}

function renderUsuarios() {
  const tbody = document.getElementById('tb-usuarios');
  if (!allUsuarios.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state"><p>Nenhum usuário</p></td></tr>`;
    return;
  }
  tbody.innerHTML = allUsuarios.map(u => {
    const perfil = u.is_admin
      ? '<span class="badge badge-admin">👑 Admin</span>'
      : '<span class="badge badge-neutral">👤 Operador</span>';
    const status = u.aprovado
      ? '<span class="badge badge-success">Ativo</span>'
      : '<span class="badge badge-warning">Pendente</span>';
    const btnApr = !u.aprovado
      ? `<button class="btn btn-success btn-sm" onclick="aprovarUsuario('${u.id}')">✅ Aprovar</button>`
      : '';
    const btnDel = u.id !== currentUser.id
      ? `<button class="btn btn-ghost btn-sm" onclick="confirmDelete('user','${u.id}','${esc(u.nome)}')" style="color:var(--danger)">🗑️</button>`
      : '';
    return `<tr>
      <td><strong>${esc(u.nome)}</strong></td>
      <td>${esc(u.email)}</td>
      <td>${perfil}</td>
      <td>${status}</td>
      <td>${fDT(u.criado_em)}</td>
      <td class="col-actions">
        <button class="btn btn-ghost btn-sm" onclick="openUserModal('${u.id}')">✏️</button>
        ${btnApr}
        ${btnDel}
      </td>
    </tr>`;
  }).join('');
}

function openUserModal(id = null) {
  document.getElementById('m-user-title').textContent = id ? 'Editar Usuário' : 'Novo Usuário';
  document.getElementById('mu-id').value = '';
  document.getElementById('mu-nome').value = '';
  document.getElementById('mu-email').value = '';
  document.getElementById('mu-senha').value = '';
  document.getElementById('mu-admin').value = 'false';
  document.getElementById('mu-senha-hint').classList.toggle('hidden', !id);

  if (id) {
    const u = allUsuarios.find(x => x.id === id);
    if (!u) return;
    document.getElementById('mu-id').value = u.id;
    document.getElementById('mu-nome').value = u.nome;
    document.getElementById('mu-email').value = u.email;
    document.getElementById('mu-admin').value = String(u.is_admin);
  }
  openModal('m-user');
}

async function saveUsuario() {
  const id = document.getElementById('mu-id').value;
  const nome = document.getElementById('mu-nome').value.trim();
  const email = document.getElementById('mu-email').value.trim();
  const senha = document.getElementById('mu-senha').value;
  const is_admin = document.getElementById('mu-admin').value === 'true';

  if (!nome) { toast('Nome é obrigatório', 'warn'); return; }
  if (!email) { toast('E-mail é obrigatório', 'warn'); return; }
  if (!id && !senha) { toast('Senha é obrigatória para novo usuário', 'warn'); return; }

  const body = { nome, email, is_admin };
  if (senha) body.senha = senha;

  try {
    if (id) {
      await api('PATCH', `/users/${id}`, body);
      toast('Usuário atualizado!');
    } else {
      await api('POST', '/users', body);
      toast('Usuário criado!');
    }
    closeModal('m-user');
    await loadUsuarios();
  } catch (e) {
    toast(e.message, 'err');
  }
}

async function aprovarUsuario(id) {
  try {
    await api('POST', `/users/${id}/aprovar`);
    toast('Usuário aprovado!');
    await loadUsuarios();
  } catch (e) {
    toast(e.message, 'err');
  }
}

async function deleteUsuario(id) {
  try {
    await api('DELETE', `/users/${id}`);
    toast('Usuário excluído!');
    await loadUsuarios();
  } catch (e) {
    toast(e.message, 'err');
  }
}

// ── Relatórios ────────────────────────────────────────────────────────────────
async function fetchDownload(url, filename) {
  try {
    const res = await fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) {
      const d = await res.json().catch(() => null);
      throw new Error(d?.detail || `Erro ${res.status}`);
    }
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename || 'relatorio';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  } catch (e) {
    toast('Erro ao baixar: ' + e.message, 'err');
  }
}

function downloadRelatorio(tipo, formato, params) {
  const qs = params ? '?' + params : '';
  const ext = formato === 'xlsx' ? 'xlsx' : 'pdf';
  const url = `${API}/relatorios/${tipo}/${formato}${qs}`;
  fetchDownload(url, `${tipo}.${ext}`);
}

function gerarComprovantes() {
  const input = document.getElementById('r-comp-data');
  const dataRef = input?.value || today();
  const url = `${API}/relatorios/comprovantes/pdf?data_ref=${dataRef}`;
  const filename = `comprovantes_cobranca_${dataRef}.pdf`;
  toast('Gerando comprovantes…', 'info');
  fetchDownload(url, filename);
}

// Preenche data padrão dos comprovantes com hoje ao carregar a aba de relatórios
function initRelatorios() {
  const el = document.getElementById('r-comp-data');
  if (el && !el.value) el.value = today();
}

// ── Pagination helper ─────────────────────────────────────────────────────────
function renderPagination(container, total, page, perPage, callback) {
  const pages = Math.ceil(total / perPage) || 1;
  if (pages <= 1 && total <= perPage) {
    container.innerHTML = `<span class="text-muted">Mostrando ${total} de ${total}</span>`;
    return;
  }
  const from = (page - 1) * perPage + 1;
  const to = Math.min(page * perPage, total);

  // Build page numbers list
  const pageNums = [];
  for (let p = 1; p <= pages; p++) {
    if (p === 1 || p === pages || Math.abs(p - page) <= 2) {
      pageNums.push({ type: 'btn', val: p });
    } else if (Math.abs(p - page) === 3 && pageNums[pageNums.length - 1]?.type !== 'ellipsis') {
      pageNums.push({ type: 'ellipsis' });
    }
  }

  container.innerHTML = `
    <span class="text-muted">Mostrando ${from}–${to} de ${total}</span>
    <div class="pagination-pages" data-pag></div>`;

  const wrap = container.querySelector('[data-pag]');

  // Prev button
  const prev = document.createElement('button');
  prev.className = 'page-btn';
  prev.textContent = '‹';
  if (page === 1) prev.disabled = true;
  prev.addEventListener('click', () => callback(page - 1));
  wrap.appendChild(prev);

  // Page buttons
  pageNums.forEach(item => {
    if (item.type === 'ellipsis') {
      const span = document.createElement('span');
      span.style.cssText = 'padding:0 .3rem;color:var(--text-muted)';
      span.textContent = '…';
      wrap.appendChild(span);
    } else {
      const btn = document.createElement('button');
      btn.className = 'page-btn' + (item.val === page ? ' active' : '');
      btn.textContent = item.val;
      btn.addEventListener('click', () => callback(item.val));
      wrap.appendChild(btn);
    }
  });

  // Next button
  const next = document.createElement('button');
  next.className = 'page-btn';
  next.textContent = '›';
  if (page === pages) next.disabled = true;
  next.addEventListener('click', () => callback(page + 1));
  wrap.appendChild(next);
}

// ── Init ──────────────────────────────────────────────────────────────────────
(function init() {
  const savedToken = sessionStorage.getItem('mp_token');
  const savedUser = sessionStorage.getItem('mp_user');
  if (savedToken && savedUser) {
    try {
      token = savedToken;
      currentUser = JSON.parse(savedUser);
      if (!currentUser.aprovado) {
        showSection('s-pending');
        return;
      }
      enterApp();
      return;
    } catch {}
  }
  showSection('s-login');
})();
