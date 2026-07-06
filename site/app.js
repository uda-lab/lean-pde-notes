/* lean-pde-notes — vanilla static viewer.
 * No framework, no bundler, no runtime deps except vendored KaTeX (global `katex`
 * and `renderMathInElement`). Data: data/nodes.json (built by scripts/build_site_data.py)
 * and data/coverage.json (scripts/coverage.py). Hash routing, all rendering client-side. */
'use strict';

const state = {
  data: null,
  coverage: null,
  bySlug: new Map(),
  byName: new Map(),      // display name -> node (first when a name collides)
  nameDict: new Map(),    // fully-qualified name -> slug (hover longest-match)
  shortDict: new Map(),   // unique simple name -> slug
  chapterMeta: new Map(), // chapter id -> {label_ja, description}
  chapterTotals: new Map(),
  trail: [],              // session navigation stack of decl slugs (breadcrumb)
};

const LEAN_KEYWORDS = new Set([
  'theorem', 'lemma', 'def', 'abbrev', 'structure', 'instance', 'inductive', 'class',
  'where', 'extends', 'deriving', 'with', 'fun', 'let', 'in', 'do', 'match', 'if',
  'then', 'else', 'by', 'have', 'show', 'from', 'calc', 'at', 'forall', 'exists',
  'Type', 'Sort', 'Prop', 'variable', 'open', 'namespace', 'end', 'noncomputable',
  'private', 'protected', 'mutual', 'attribute', 'set_option', 'exact', 'intro',
  'apply', 'refine', 'rw', 'simp',
]);

/* ---------------- utilities ---------------- */

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function el(tag, attrs, children) {
  const node = document.createElement(tag);
  if (attrs) {
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null) continue;
      if (k === 'class') node.className = v;
      else if (k === 'html') node.innerHTML = v;
      else if (k === 'text') node.textContent = v;
      else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v);
    }
  }
  if (children != null) {
    for (const c of [].concat(children)) {
      if (c == null) continue;
      node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
  }
  return node;
}

function badge(cls, label) { return el('span', { class: 'badge ' + cls, text: label }); }

function kindBadge(kind) { return badge('kind-' + kind, kind); }
function gapBadge(level) {
  const map = { none: 'gap: なし', mild: 'gap: 小', large: 'gap: 大' };
  return badge('gap-' + level, map[level] || ('gap: ' + level));
}
function tierBadge(tier) { return badge('tier-' + tier, tier === 'full' ? 'フル注釈' : 'グロス'); }

function declHref(slug) { return '#/decl/' + encodeURIComponent(slug); }
function chapterHref(id) { return '#/chapter/' + encodeURIComponent(id); }

function renderProse(container, text) {
  container.textContent = text || '';
  if (typeof renderMathInElement === 'function') {
    try {
      renderMathInElement(container, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
        ],
        throwOnError: false,
      });
    } catch (e) { /* leave raw text on failure */ }
  }
}

function firstLine(text, n) {
  if (!text) return '';
  const lines = String(text).trim().split('\n').filter(l => l.trim());
  return lines.slice(0, n || 1).join(' ');
}

/* Lightweight Lean highlighter + hover-ref linker (keywords / comments / strings /
 * attributes; identifiers matched against the name dictionary get a ref underline). */
function highlightLean(src) {
  let out = '';
  let i = 0;
  const n = src.length;
  const identRe = /^[A-Za-z_Ͱ-￿][A-Za-z0-9_'.Ͱ-￿]*/;
  while (i < n) {
    const rest = src.slice(i);
    if (rest.startsWith('/-')) {
      let j = src.indexOf('-/', i + 2);
      j = j < 0 ? n : j + 2;
      out += '<span class="lean-cm">' + esc(src.slice(i, j)) + '</span>'; i = j; continue;
    }
    if (rest.startsWith('--')) {
      let j = src.indexOf('\n', i); j = j < 0 ? n : j;
      out += '<span class="lean-cm">' + esc(src.slice(i, j)) + '</span>'; i = j; continue;
    }
    if (rest.startsWith('@[')) {
      let j = src.indexOf(']', i); j = j < 0 ? n : j + 1;
      out += '<span class="lean-at">' + esc(src.slice(i, j)) + '</span>'; i = j; continue;
    }
    if (src[i] === '"') {
      let j = i + 1;
      while (j < n && src[j] !== '"') { if (src[j] === '\\') j++; j++; }
      j = Math.min(j + 1, n);
      out += '<span class="lean-st">' + esc(src.slice(i, j)) + '</span>'; i = j; continue;
    }
    const m = identRe.exec(rest);
    if (m) {
      const w = m[0];
      if (LEAN_KEYWORDS.has(w)) {
        out += '<span class="lean-kw">' + esc(w) + '</span>';
      } else {
        const slug = refSlugFor(w);
        if (slug) out += '<span class="ref" data-slug="' + esc(slug) + '">' + esc(w) + '</span>';
        else out += esc(w);
      }
      i += w.length; continue;
    }
    out += esc(src[i]); i++;
  }
  return out;
}

function refSlugFor(token) {
  if (state.nameDict.has(token)) return state.nameDict.get(token);
  if (state.shortDict.has(token)) return state.shortDict.get(token);
  return null;
}

/* ---------------- data loading ---------------- */

async function loadData() {
  const [nodesRes, covRes] = await Promise.all([
    fetch('data/nodes.json').then(r => r.ok ? r.json() : Promise.reject(r.status)),
    fetch('data/coverage.json').then(r => r.ok ? r.json() : null).catch(() => null),
  ]);
  state.data = nodesRes;
  state.coverage = covRes;

  for (const node of nodesRes.nodes) {
    state.bySlug.set(node.slug, node);
    if (!state.byName.has(node.name)) state.byName.set(node.name, node);
    state.nameDict.set(node.name, node.slug);
    state.chapterTotals.set(node.chapter, (state.chapterTotals.get(node.chapter) || 0) + 1);
  }
  // unique simple names only (avoid mis-linking ambiguous short names)
  const shortCount = new Map();
  for (const node of nodesRes.nodes) shortCount.set(node.shortName, (shortCount.get(node.shortName) || 0) + 1);
  for (const node of nodesRes.nodes) {
    if (shortCount.get(node.shortName) === 1) state.shortDict.set(node.shortName, node.slug);
  }
  for (const ch of (nodesRes.chapters || [])) state.chapterMeta.set(ch.id, ch);

  const meta = document.getElementById('footer-meta');
  meta.textContent = `${nodesRes.decl_count} 宣言 / ${nodesRes.annotated_count} 注釈済み`
    + (nodesRes.pin ? ` · lean-pde @ ${nodesRes.pin.slice(0, 10)}` : '')
    + (nodesRes.has_full_metadata ? '' : ' · (fallback universe: シグネチャ・依存辺なし)');
}

/* ---------------- routing ---------------- */

function route() {
  const hash = location.hash || '#/';
  const parts = hash.replace(/^#\/?/, '').split('/');
  const app = document.getElementById('app');
  app.innerHTML = '';
  hideHoverCard();

  const head = parts[0] || '';
  try {
    if (head === '' ) renderHome(app);
    else if (head === 'decl') renderDecl(app, decodeURIComponent(parts.slice(1).join('/')));
    else if (head === 'chapter') renderChapter(app, decodeURIComponent(parts[1] || ''));
    else if (head === 'dag') renderDag(app);
    else if (head === 'coverage') renderCoverage(app);
    else if (head === 'search') renderSearch(app, decodeURIComponent(parts.slice(1).join('/')));
    else app.appendChild(el('p', { text: 'ページが見つかりません。' }));
  } catch (e) {
    app.appendChild(el('pre', { class: 'lean', text: 'レンダリングエラー: ' + (e && e.message) }));
    console.error(e);
  }
  window.scrollTo(0, 0);
}

/* ---------------- home ---------------- */

function renderHome(app) {
  app.appendChild(el('h1', { text: 'Leray–Hopf 形式化 対訳ノート' }));
  app.appendChild(el('p', {
    class: 'prose',
    text: 'uda-lab/lean-pde の全宣言に Lean コードと日本語の数学解説を並置する純静的ビューア。'
      + 'capstone から証明ツリーを辿り、依存補題をその場で展開できる。',
  }));

  // capstone cards
  const grid = el('div', { class: 'capstone-grid' });
  for (const slug of (state.data.capstones || [])) {
    const node = state.bySlug.get(slug);
    if (!node) continue;
    const card = el('div', { class: 'card' }, [
      el('div', { class: 'meta-row' }, [kindBadge(node.kind), gapBadge(node.corpus ? node.corpus.gap.level : 'none')]),
      el('h3', { text: node.chapter === 'capstone-torus' ? '𝕋³ 主定理' : 'ℝ³ 主定理' }),
      el('a', { class: 'mono', href: declHref(slug), text: node.name }),
    ]);
    if (node.corpus) {
      const p = el('div', { class: 'prose' });
      p.style.marginTop = '0.5rem';
      renderProse(p, firstLine(node.corpus.statement_ja, 2));
      card.appendChild(p);
    }
    grid.appendChild(card);
  }
  app.appendChild(grid);

  // coverage mini
  if (state.coverage) {
    const c = state.coverage;
    const wrap = el('div', { class: 'section' }, [el('h3', { text: 'カバレッジ' })]);
    wrap.appendChild(progressBar(c.pct_annotated));
    wrap.appendChild(el('p', {
      class: 'filemeta',
      text: `${c.annotated} / ${c.total_decls} 注釈済み (${c.pct_annotated}%) · full ${c.full} · gloss ${c.gloss}`,
    }));
    wrap.appendChild(el('p', {}, [el('a', { href: '#/coverage', text: '章別カバレッジを見る →' })]));
    app.appendChild(wrap);
  }

  // chapter list
  const sec = el('div', { class: 'section' }, [el('h3', { text: '章' })]);
  const list = el('div', { class: 'chapter-list' });
  for (const ch of (state.data.chapters || [])) {
    const total = state.chapterTotals.get(ch.id) || 0;
    list.appendChild(el('a', { href: chapterHref(ch.id) }, [
      el('span', { text: ch.label_ja || ch.id }),
      el('span', { class: 'count', text: String(total) }),
    ]));
  }
  sec.appendChild(list);
  app.appendChild(sec);
}

function progressBar(pct) {
  const bar = el('div', { class: 'progress' });
  bar.appendChild(el('span', { style: `width:${Math.max(0, Math.min(100, pct))}%` }));
  return bar;
}

/* ---------------- node page ---------------- */

function updateTrail(slug) {
  const node = state.bySlug.get(slug);
  const idx = state.trail.indexOf(slug);
  if (idx >= 0) {
    state.trail = state.trail.slice(0, idx + 1);           // back-navigation
  } else if (state.trail.length && node) {
    const parent = state.bySlug.get(state.trail[state.trail.length - 1]);
    if (parent && parent.uses.includes(slug)) state.trail.push(slug);  // drilling down
    else state.trail = [slug];
  } else {
    state.trail = [slug];                                  // fresh entry / reload
  }
}

function breadcrumb(node) {
  const bc = el('div', { class: 'breadcrumb' });
  bc.appendChild(el('a', { href: '#/', text: 'ホーム' }));
  const chId = node.chapter;
  const chMeta = state.chapterMeta.get(chId);
  bc.appendChild(el('span', { class: 'sep', text: '›' }));
  bc.appendChild(el('a', { href: chapterHref(chId), text: (chMeta && chMeta.label_ja) || chId }));
  for (const slug of state.trail) {
    const nn = state.bySlug.get(slug);
    if (!nn) continue;
    bc.appendChild(el('span', { class: 'sep', text: '›' }));
    if (slug === node.slug) bc.appendChild(el('span', { text: nn.shortName }));
    else bc.appendChild(el('a', { href: declHref(slug), text: nn.shortName }));
  }
  return bc;
}

function renderDecl(app, slug) {
  const node = state.bySlug.get(slug);
  if (!node) { app.appendChild(el('p', { text: '宣言が見つかりません: ' + slug })); return; }
  updateTrail(slug);

  app.appendChild(breadcrumb(node));

  const title = el('h1', { class: 'decl-title' }, [el('span', { class: 'short', text: node.shortName })]);
  app.appendChild(title);

  const meta = el('div', { class: 'meta-row' }, [
    kindBadge(node.kind),
    node.corpus ? gapBadge(node.corpus.gap.level) : null,
    node.corpus ? tierBadge(node.corpus.tier) : badge('tier-gloss', '未注釈'),
    node.private ? badge('priv', 'private') : null,
    node.corpus && node.corpus.sample ? badge('sample', 'sample') : null,
  ]);
  const chMeta = state.chapterMeta.get(node.chapter);
  meta.appendChild(el('a', { class: 'badge', href: chapterHref(node.chapter), text: (chMeta && chMeta.label_ja) || node.chapter }));
  app.appendChild(meta);
  app.appendChild(el('p', { class: 'mono filemeta', text: `${node.name}  ·  ${node.file}:${node.startLine}` }));

  // Note panel (large gap) above the proof band
  if (node.corpus && node.corpus.gap.level === 'large' && node.corpus.gap.note) {
    const np = el('div', { class: 'note-panel' }, [el('h4', { text: '形式化ギャップ (Note)' })]);
    const body = el('div', { class: 'prose' });
    renderProse(body, node.corpus.gap.note);
    np.appendChild(body);
    app.appendChild(np);
  }

  // Statement band: signature (Lean) ⇄ statement_ja
  app.appendChild(el('div', { class: 'section' }, [el('h3', { text: '主張' })]));
  const stmtBand = el('div', { class: 'twocol jp-first' }, [
    leanPane('シグネチャ', node.signature || '(シグネチャなし — fallback universe)', node),
    jpPane('日本語', node.corpus ? node.corpus.statement_ja : null, '未注釈（statement_ja がまだありません）'),
  ]);
  app.appendChild(stmtBand);

  // Proof band: Lean proof body (collapsed) ⇄ proof_ja
  const isThmLike = node.kind === 'theorem' || node.kind === 'lemma';
  if (isThmLike || (node.corpus && node.corpus.proof_ja)) {
    app.appendChild(el('div', { class: 'section' }, [el('h3', { text: '証明' })]));
    const leanProof = el('div', { class: 'pane lean' });
    leanProof.appendChild(el('h4', { text: 'Lean 証明本文' }));
    const det = el('details', { class: 'use' });
    const inner = el('div', { class: 'use-body' });
    if (node.has_source && node.source) {
      // verbatim declaration source (embedded at build time via --lean-root), collapsed by default
      det.appendChild(el('summary', {}, [
        el('span', { class: 'summary-name', text: 'ソースを表示' }),
        el('span', { class: 'filemeta', text: `${node.file}:${node.startLine}–${node.endLine}` }),
      ]));
      const wrap = el('div', { class: 'codewrap' });
      wrap.appendChild(el('pre', { class: 'lean source', html: highlightLean(node.source) }));
      inner.appendChild(wrap);
    } else {
      // fallback: no lean-root at build time — show doc-comment + source location reference
      det.appendChild(el('summary', {}, [el('span', { class: 'summary-name', text: 'ソース参照' })]));
      if (node.doc) {
        const dp = el('div', { class: 'prose' });
        dp.style.whiteSpace = 'pre-wrap';
        dp.textContent = node.doc;
        inner.appendChild(dp);
      }
      inner.appendChild(el('p', {
        class: 'filemeta',
        text: `このビルドはソース本文を埋め込んでいません（--lean-root なし）。位置: `
          + `${node.file}:${node.startLine}–${node.endLine}`,
      }));
    }
    det.appendChild(inner);
    leanProof.appendChild(det);

    const proofBand = el('div', { class: 'twocol jp-first' }, [
      leanProof,
      jpPane('日本語証明', node.corpus ? node.corpus.proof_ja : null,
        node.corpus ? 'この tier では proof_ja は省略されています。' : '未注釈'),
    ]);
    app.appendChild(proofBand);
  }

  // uses (direct deps) — depth-1 accordion
  renderUses(app, node);
  // used-by (links only)
  renderUsedBy(app, node);

  // KaTeX + hover binding
  bindHoverCards(app);
}

function leanPane(label, code, node) {
  const pane = el('div', { class: 'pane lean' });
  pane.appendChild(el('h4', { text: label }));
  const wrap = el('div', { class: 'codewrap' });
  const pre = el('pre', { class: 'lean', html: highlightLean(code) });
  wrap.appendChild(pre);
  pane.appendChild(wrap);
  if (node) pane.appendChild(el('div', { class: 'filemeta', text: `${node.file}:${node.startLine}` }));
  return pane;
}

function jpPane(label, text, emptyMsg) {
  const pane = el('div', { class: 'pane jp' });
  pane.appendChild(el('h4', { text: label }));
  if (text && String(text).trim()) {
    const p = el('div', { class: 'prose' });
    renderProse(p, text);
    pane.appendChild(p);
  } else {
    pane.appendChild(el('div', { class: 'prose empty', text: emptyMsg || '未注釈' }));
  }
  return pane;
}

function renderUses(app, node) {
  const sec = el('div', { class: 'section' }, [el('h3', { text: `依存補題 uses (${node.uses.length})` })]);
  if (!node.uses.length) sec.appendChild(el('p', { class: 'filemeta', text: '直接依存なし。' }));
  for (const slug of node.uses) {
    const dep = state.bySlug.get(slug);
    if (!dep) continue;
    const det = el('details', { class: 'use' });
    const summary = el('summary', {}, [
      kindBadge(dep.kind),
      el('span', { class: 'summary-name', text: dep.shortName }),
      dep.corpus ? gapBadge(dep.corpus.gap.level) : badge('tier-gloss', '未注釈'),
    ]);
    det.appendChild(summary);
    // depth-1 body: statement_ja + signature + "open" link (NO nested accordion)
    const body = el('div', { class: 'use-body' });
    if (dep.corpus && dep.corpus.statement_ja) {
      const p = el('div', { class: 'prose' });
      renderProse(p, dep.corpus.statement_ja);
      body.appendChild(p);
    }
    const sigWrap = el('div', { class: 'codewrap' });
    sigWrap.appendChild(el('pre', { class: 'lean', html: highlightLean(dep.signature || '(シグネチャなし)') }));
    body.appendChild(sigWrap);
    body.appendChild(el('p', {}, [el('a', { href: declHref(slug), text: 'このノードを開く →' })]));
    det.appendChild(body);
    sec.appendChild(det);
  }
  app.appendChild(sec);
}

function renderUsedBy(app, node) {
  const sec = el('div', { class: 'section' }, [el('h3', { text: `被依存 used-by (${node.usedBy.length})` })]);
  if (!node.usedBy.length) { sec.appendChild(el('p', { class: 'filemeta', text: 'このノードを直接使う宣言はありません（capstone か葉）。' })); app.appendChild(sec); return; }
  const ul = el('ul', { class: 'usedby-list' });
  for (const slug of node.usedBy.slice(0, 400)) {
    const dep = state.bySlug.get(slug);
    if (!dep) continue;
    ul.appendChild(el('li', {}, [el('a', { href: declHref(slug), text: dep.shortName })]));
  }
  sec.appendChild(ul);
  if (node.usedBy.length > 400) sec.appendChild(el('p', { class: 'filemeta', text: `…他 ${node.usedBy.length - 400} 件` }));
  app.appendChild(sec);
}

/* ---------------- chapter page ---------------- */

const DEF_KINDS = new Set(['def', 'structure', 'abbrev', 'instance']);
const THM_KINDS = new Set(['theorem', 'lemma']);

function renderChapter(app, chId) {
  const chMeta = state.chapterMeta.get(chId);
  app.appendChild(el('div', { class: 'breadcrumb' }, [
    el('a', { href: '#/', text: 'ホーム' }), el('span', { class: 'sep', text: '›' }),
    el('span', { text: (chMeta && chMeta.label_ja) || chId }),
  ]));
  app.appendChild(el('h1', { text: (chMeta && chMeta.label_ja) || chId }));
  if (chMeta && chMeta.description) app.appendChild(el('p', { class: 'prose', text: chMeta.description }));

  const nodes = state.data.nodes.filter(n => n.chapter === chId);
  const pub = nodes.filter(n => !n.private);
  const priv = nodes.filter(n => n.private);

  const defs = pub.filter(n => DEF_KINDS.has(n.kind)).sort(byName);
  const thms = pub.filter(n => THM_KINDS.has(n.kind)).sort(byName);
  const other = pub.filter(n => !DEF_KINDS.has(n.kind) && !THM_KINDS.has(n.kind)).sort(byName);

  app.appendChild(declGroup('定義群 (def / structure / abbrev / instance)', defs));
  app.appendChild(declGroup('定理群 (theorem / lemma)', thms.concat(other)));

  // private helpers grouped per-file (collapsed) — not surfaced directly under the chapter
  if (priv.length) {
    const sec = el('div', { class: 'section' }, [el('h3', { text: `補助補題 (private, ${priv.length})` })]);
    const byFile = new Map();
    for (const n of priv) { if (!byFile.has(n.file)) byFile.set(n.file, []); byFile.get(n.file).push(n); }
    for (const file of Array.from(byFile.keys()).sort()) {
      const group = byFile.get(file).sort(byName);
      const det = el('details', { class: 'filegroup' });
      det.appendChild(el('summary', { text: `${file} (${group.length})` }));
      for (const n of group) det.appendChild(declRow(n));
      sec.appendChild(det);
    }
    app.appendChild(sec);
  }
}

function byName(a, b) { return a.shortName.localeCompare(b.shortName); }

function declGroup(title, nodes) {
  const sec = el('div', { class: 'section' }, [el('h3', { text: `${title} — ${nodes.length}` })]);
  if (!nodes.length) sec.appendChild(el('p', { class: 'filemeta', text: '該当なし。' }));
  for (const n of nodes) sec.appendChild(declRow(n));
  return sec;
}

function declRow(n) {
  const row = el('div', { class: 'decl-row' }, [
    kindBadge(n.kind),
    el('a', { class: 'name', href: declHref(n.slug), text: n.shortName }),
  ]);
  if (n.corpus) {
    const one = el('span', { class: 'one-line' });
    renderProse(one, firstLine(n.corpus.statement_ja, 1));
    row.appendChild(one);
    row.appendChild(gapBadge(n.corpus.gap.level));
    row.appendChild(tierBadge(n.corpus.tier));
  } else {
    row.appendChild(el('span', { class: 'one-line', text: '（未注釈）' }));
  }
  return row;
}

/* ---------------- DAG page ---------------- */

function renderDag(app) {
  app.appendChild(el('h1', { text: '証明ツリー (DAG)' }));
  app.appendChild(el('p', {
    class: 'prose',
    text: '2 つの capstone を根に、依存補題 (uses) をクリックで段階的に展開する。'
      + '1,412 ノード全体は描画しない（段階的開示のみ）。',
  }));
  const container = el('div', { class: 'dag' });
  const rootUl = el('ul');
  for (const slug of (state.data.capstones || [])) {
    const node = state.bySlug.get(slug);
    if (node) rootUl.appendChild(dagItem(node, new Set([slug])));
  }
  container.appendChild(rootUl);
  app.appendChild(container);
  bindHoverCards(app);
}

function dagItem(node, ancestors) {
  const li = el('li');
  const hasChildren = node.uses.length > 0;
  const twist = el('span', { class: 'twist' + (hasChildren ? '' : ' leaf'), text: hasChildren ? '▸' : '·' });
  const row = el('div', { class: 'node-row' }, [
    twist,
    kindBadge(node.kind),
    el('a', { class: 'dag-name', href: declHref(node.slug), text: node.shortName }),
    node.corpus ? gapBadge(node.corpus.gap.level) : null,
    badge('annotated', node.corpus ? '注釈済' : '—'),
  ]);
  li.appendChild(row);

  if (hasChildren) {
    let childUl = null;
    twist.addEventListener('click', () => {
      if (childUl) { const open = childUl.style.display !== 'none'; childUl.style.display = open ? 'none' : ''; twist.textContent = open ? '▸' : '▾'; return; }
      childUl = el('ul');
      for (const slug of node.uses) {
        const child = state.bySlug.get(slug);
        if (!child) continue;
        if (ancestors.has(slug)) { // avoid cycle re-expansion in this branch
          childUl.appendChild(el('li', {}, [el('div', { class: 'node-row' }, [
            el('span', { class: 'twist leaf', text: '↻' }),
            el('a', { class: 'dag-name', href: declHref(slug), text: child.shortName }),
          ])]));
          continue;
        }
        const next = new Set(ancestors); next.add(slug);
        childUl.appendChild(dagItem(child, next));
      }
      li.appendChild(childUl);
      twist.textContent = '▾';
    });
  }
  return li;
}

/* ---------------- coverage page ---------------- */

function renderCoverage(app) {
  app.appendChild(el('h1', { text: 'カバレッジ' }));
  const c = state.coverage;
  if (!c) { app.appendChild(el('p', { text: 'coverage.json を読み込めませんでした。' })); return; }
  app.appendChild(progressBar(c.pct_annotated));
  app.appendChild(el('p', { class: 'filemeta', text: `全体: ${c.annotated} / ${c.total_decls} (${c.pct_annotated}%) · full ${c.full} · gloss ${c.gloss}` }));

  const table = el('table', { class: 'coverage' });
  table.appendChild(el('tr', {}, [
    el('th', { text: '章' }), el('th', { class: 'num', text: '総数' }),
    el('th', { class: 'num', text: '注釈済' }), el('th', { class: 'num', text: 'full' }),
    el('th', { class: 'num', text: 'gloss' }), el('th', { class: 'num', text: '%' }),
  ]));
  for (const ch of (state.data.chapters || [])) {
    const stat = (c.chapters && c.chapters[ch.id]) || { annotated: 0, full: 0, gloss: 0 };
    const total = state.chapterTotals.get(ch.id) || 0;
    const pct = total ? Math.round(1000 * stat.annotated / total) / 10 : 0;
    table.appendChild(el('tr', {}, [
      el('td', {}, [el('a', { href: chapterHref(ch.id), text: ch.label_ja || ch.id })]),
      el('td', { class: 'num', text: String(total) }),
      el('td', { class: 'num', text: String(stat.annotated) }),
      el('td', { class: 'num', text: String(stat.full) }),
      el('td', { class: 'num', text: String(stat.gloss) }),
      el('td', { class: 'num', text: pct + '%' }),
    ]));
  }
  app.appendChild(table);
}

/* ---------------- search ---------------- */

function renderSearch(app, q) {
  app.appendChild(el('h1', { text: '検索' }));
  const input = document.getElementById('search-input');
  if (input && input.value !== q) input.value = q;
  q = (q || '').trim();
  if (!q) { app.appendChild(el('p', { class: 'filemeta', text: '検索語を入力してください。' })); return; }

  const ql = q.toLowerCase();
  const hits = [];
  for (const n of state.data.nodes) {
    const nameHit = n.name.toLowerCase().includes(ql) || n.shortName.toLowerCase().startsWith(ql);
    const stmtHit = n.corpus && n.corpus.statement_ja && n.corpus.statement_ja.includes(q);
    if (nameHit || stmtHit) hits.push(n);
  }
  app.appendChild(el('p', { class: 'filemeta', text: `"${q}" — ${hits.length} 件` }));

  const groups = new Map();
  for (const n of hits) { if (!groups.has(n.kind)) groups.set(n.kind, []); groups.get(n.kind).push(n); }
  for (const kind of Array.from(groups.keys()).sort()) {
    const arr = groups.get(kind).sort(byName).slice(0, 200);
    const sec = el('div', { class: 'section' }, [el('h3', {}, [kindBadge(kind), el('span', { text: ` (${groups.get(kind).length})` })])]);
    for (const n of arr) sec.appendChild(declRow(n));
    app.appendChild(sec);
  }
}

/* ---------------- hover cards ---------------- */

let hoverTimer = null;

function bindHoverCards(root) {
  root.addEventListener('mouseover', ev => {
    const t = ev.target.closest && ev.target.closest('.ref');
    if (!t) return;
    showHoverCard(t);
  });
  root.addEventListener('mouseout', ev => {
    const t = ev.target.closest && ev.target.closest('.ref');
    if (!t) return;
    hoverTimer = setTimeout(hideHoverCard, 180);
  });
  root.addEventListener('click', ev => {
    const t = ev.target.closest && ev.target.closest('.ref');
    if (!t) return;
    ev.preventDefault();          // touch / tap: show the card instead of jumping
    showHoverCard(t, true);
  });
}

function showHoverCard(refEl, pin) {
  clearTimeout(hoverTimer);
  const slug = refEl.getAttribute('data-slug');
  const node = state.bySlug.get(slug);
  if (!node) return;
  const card = document.getElementById('hovercard');
  card.innerHTML = '';
  card.appendChild(el('div', { class: 'meta-row' }, [
    kindBadge(node.kind),
    node.corpus ? gapBadge(node.corpus.gap.level) : null,
  ]));
  card.appendChild(el('div', { class: 'hc-sig', text: firstLine(node.signature, 1) || node.name }));
  if (node.corpus && node.corpus.statement_ja) {
    const s = el('div', { class: 'hc-stmt' });
    renderProse(s, firstLine(node.corpus.statement_ja, 2));
    card.appendChild(s);
  }
  card.appendChild(el('div', {}, [el('a', { href: declHref(slug), text: node.shortName + ' を開く →' })]));

  const r = refEl.getBoundingClientRect();
  card.hidden = false;
  const top = r.bottom + 6;
  const left = Math.min(r.left, window.innerWidth - card.offsetWidth - 12);
  card.style.top = top + 'px';
  card.style.left = Math.max(8, left) + 'px';
  card.onmouseenter = () => clearTimeout(hoverTimer);
  card.onmouseleave = () => { if (!pin) hideHoverCard(); };
}

function hideHoverCard() {
  const card = document.getElementById('hovercard');
  if (card) card.hidden = true;
}

/* ---------------- boot ---------------- */

function setupSearch() {
  const form = document.getElementById('search-form');
  const input = document.getElementById('search-input');
  form.addEventListener('submit', ev => {
    ev.preventDefault();
    const q = input.value.trim();
    location.hash = q ? '#/search/' + encodeURIComponent(q) : '#/';
  });
}

async function boot() {
  setupSearch();
  try {
    await loadData();
  } catch (e) {
    document.getElementById('app').innerHTML =
      '<p>データ (data/nodes.json) を読み込めませんでした。<br>'
      + 'scripts/build_site_data.py を実行してから <code>python3 -m http.server</code> で配信してください。</p>';
    console.error(e);
    return;
  }
  window.addEventListener('hashchange', route);
  route();
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
