/* leray-hopf-notes — vanilla static viewer.
 * No framework, no bundler, no runtime deps except vendored KaTeX (global `katex`
 * and `renderMathInElement`). Data: data/nodes.json and lazy data/sources.json
 * (built by scripts/build_site_data.py), plus data/coverage.json (scripts/coverage.py).
 * Hash routing, all rendering client-side. */
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
  sources: null,           // slug -> verbatim Lean source, loaded lazily from data/sources.json
  sourcesPromise: null,
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

// notes#72: also escape quotes, not just &<>. highlightLean() interpolates
// esc(slug) directly into a quoted HTML attribute (`data-slug="' + esc(slug) + '"'`),
// not just element text content — escaping only &<> there is brittle attribute
// interpolation, even though the current Lean identifier grammar (extracted/decls.json
// names) cannot produce a `"` or `'` today, so it isn't currently exploitable.
function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// notes#72: prefers-reduced-motion-aware scrollIntoView wrapper, used by every
// scroll-link in the app (gap-note jump, /about bibliography highlight) so users who
// have asked the OS for reduced motion never get a forced smooth-scroll animation.
function scrollIntoViewSafe(el) {
  if (!el || typeof el.scrollIntoView !== 'function') return;
  const reduceMotion = typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  el.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
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

function badge(cls, label, title) {
  const b = el('span', { class: 'badge ' + cls, text: label });
  if (title) b.title = title;
  return b;
}

function kindBadge(kind) { return badge('kind-' + kind, kind); }
function gapBadge(level) {
  // notes#65: labelled "コスト" (formalization overhead), NOT "gap" — a large value here is
  // orthogonal to proof completion (a fully verified theorem can still have a large
  // formalization-overhead cost). Proof completion is proofStatusBadge()'s job.
  const map = { none: 'コスト: なし', mild: 'コスト: 小', large: 'コスト: 大' };
  return badge('gap-' + level, map[level] || ('コスト: ' + level),
    '形式化コスト：Lean 証明が自然言語の議論よりどれだけ冗長になるかの目安。証明状態（sorry の有無など）は別の指標。');
}
function tierBadge(tier) {
  return badge('tier-' + tier, tier === 'full' ? 'フル注釈' : 'グロス',
    '「tier」は解説の詳しさ（annotation depth）を表す。証明が完了・検証済みであることを保証するものではない — 証明状態は別バッジを参照。');
}

// notes#65: proof_status is independent of tier/gap. Absence (or 'verified') means "no
// known literal sorry, no known false/over-general statement, not a historical scaffold or
// retired declaration" — nothing is rendered for that default case so a normal proved
// theorem keeps its ordinary look. Every other status gets an unmistakable, differently
// colored badge (proofStatusBadge) PLUS a banner box on the declaration page
// (proofStatusBanner) so a sorry-carrying or quarantined statement never reads like a
// proved theorem.
const PROOF_STATUS_META = {
  'contains-sorry': { label: 'sorry あり', cls: 'proof-sorry',
    desc: '証明本文に未証明の `sorry`（または sorry に依存する補題）が残っている。主張は真であることが期待されているが機械的に検証されていない。' },
  'scaffold': { label: '足場（歴史的）', cls: 'proof-scaffold',
    desc: '開発初期に置かれたプレースホルダ宣言。現在の証明経路の一部ではなく、歴史的記録として残されている。' },
  'retired': { label: '廃止', cls: 'proof-retired',
    desc: '公開版の証明範囲からは除外・置き換え済み。来歴のために本コーパスに残している。' },
  'invalid-statement': { label: '主張に誤り（隔離中）', cls: 'proof-invalid',
    desc: '記載されている型のままでは主張が偽、または一般化しすぎている。ソース側の修正待ちで隔離されている。' },
};

function proofStatusBadge(status) {
  const meta = PROOF_STATUS_META[status];
  if (!meta) return null; // 'verified' (or absent) — no badge, looks like an ordinary proved theorem.
  return badge('proof-status ' + meta.cls, meta.label, meta.desc);
}

// Prominent banner (not just a small badge) so a sorry-carrying / quarantined / scaffold /
// retired statement cannot be mistaken for a normal proved theorem at a glance.
function proofStatusBanner(status) {
  const meta = PROOF_STATUS_META[status];
  if (!meta) return null;
  return el('div', { class: 'proof-status-banner ' + meta.cls, role: 'note' }, [
    el('strong', { text: meta.label }),
    el('span', { text: ' — ' + meta.desc }),
  ]);
}

function declHref(slug) { return '#/decl/' + encodeURIComponent(slug); }
function chapterHref(id) { return '#/chapter/' + encodeURIComponent(id); }

// notes#68: exact-PIN GitHub blob permalink for a Lean source location, so "where does
// this come from" resolves to the literal pinned commit, not a moving `main` branch.
// Returns null when the source repository or PIN isn't known (e.g. fallback universe).
function sourceBlobHref(file, startLine, endLine) {
  const repo = state.data.citation && state.data.citation.source_repository;
  const pin = state.data.pin;
  if (!repo || !pin || !file) return null;
  if (!(Number.isInteger(startLine) && startLine > 0)) return null;
  const hasEnd = Number.isInteger(endLine) && endLine >= startLine && endLine !== startLine;
  const frag = hasEnd ? `#L${startLine}-L${endLine}` : `#L${startLine}`;
  return `${repo}/blob/${pin}/${file}${frag}`;
}

// Renders `file:startLine[–endLine]` as a link to the exact-PIN GitHub blob when
// possible, falling back to plain text (same visual style either way).
function fileLineNode(cls, file, startLine, endLine, prefix) {
  const rangeText = (endLine && endLine !== startLine) ? `${startLine}–${endLine}` : `${startLine}`;
  const text = `${prefix || ''}${file}:${rangeText}`;
  const href = sourceBlobHref(file, startLine, endLine);
  if (href) {
    return el('a', { class: cls, href, target: '_blank', rel: 'noopener', text });
  }
  return el('span', { class: cls, text });
}

/* ---------------- prose rendering (D1 paragraphs + D5 inline tokenizer) ----------------
 *
 * Prose fields (statement_ja / proof_ja / gap.note) are authored one physical line per
 * paragraph, blank line = paragraph boundary (notes#12 D1). The renderer:
 *   1. splits on blank lines into <p> paragraphs (NO width/height/char truncation);
 *   2. within a paragraph, extracts $…$ / $$…$$ math segments FIRST so the inline
 *      tokenizer never touches TeX;
 *   3. tokenizes the non-math text for `code`, **strong**, [[ref]] / [[ref|target]]
 *      (D5) building DOM nodes only — never innerHTML of raw corpus text (escape-safe);
 *   4. re-runs KaTeX over the assembled container so the math text nodes render.
 * Legacy single \n inside a paragraph are joined without a break (CJK↔CJK: no space;
 * ASCII-word↔ASCII-word: one space) — the欧文 join rule is NOT applied across CJK. */

const HOVER_PREVIEW_BUDGET = 90;   // hovercard sentence-preview budget (code points)
const ROW_PREVIEW_BUDGET = 78;     // chapter/search one-line preview budget
const META_DESCRIPTION_BUDGET = 140; // <meta name="description"> sentence-preview budget

function typesetMath(container) {
  if (typeof renderMathInElement !== 'function') return;
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

// Split prose into paragraph strings on blank lines. Each may still carry legacy
// single newlines (joined later). No length-based cutting anywhere.
function splitParagraphs(text) {
  if (!text) return [];
  return String(text).replace(/\r\n?/g, '\n').split(/\n[ \t]*\n/)
    .map(p => p.replace(/^\n+|\n+$/g, '')).filter(p => p.trim().length);
}

// Glue two sides of a collapsed newline: one space only when both are ASCII word
// chars; CJK (or mixed) joins with no space.
function joinGlue(before, after) {
  const w = /[0-9A-Za-z]/;
  return before && after && w.test(before) && w.test(after) ? ' ' : '';
}

// Collapse legacy hard-wrap newlines inside one text run (math already excised).
function joinSoftLines(s) {
  return s.replace(/[ \t]*\n[ \t]*/g, (m, offset, str) =>
    joinGlue(str[offset - 1] || '', str[offset + m.length] || ''));
}

// Segment a single paragraph into math / non-math runs. Math delimiters mirror KaTeX
// auto-render ($$ display, $ inline); an unterminated $ is treated as literal text.
function segmentMath(par) {
  const segs = [];
  let i = 0, buf = '';
  const n = par.length;
  const flush = () => { if (buf) { segs.push({ math: false, text: buf }); buf = ''; } };
  while (i < n) {
    if (par[i] === '$') {
      const display = par[i + 1] === '$';
      const delim = display ? '$$' : '$';
      let j = i + delim.length, found = -1;
      while (j < n) {
        if (display ? (par[j] === '$' && par[j + 1] === '$') : par[j] === '$') { found = j; break; }
        j++;
      }
      if (found >= 0) {
        flush();
        segs.push({ math: true, raw: par.slice(i, found + delim.length) });
        i = found + delim.length;
        continue;
      }
    }
    buf += par[i]; i++;
  }
  flush();
  return segs;
}

// Resolve a [[…|target]] reference target (display name / fq name / slug / short name)
// to a node slug, else null.
function refSlugForRefToken(t) {
  if (!t) return null;
  if (state.bySlug.has(t)) return t;
  if (state.nameDict.has(t)) return state.nameDict.get(t);
  if (state.shortDict.has(t)) return state.shortDict.get(t);
  if (state.nameDict.has('LerayHopf.' + t)) return state.nameDict.get('LerayHopf.' + t);
  return null;
}

// Math is masked to NUL-delimited placeholders before inline tokenizing so that
// **strong** / `code` / [[ref]] may enclose a $…$ span without the delimiter splitting
// the markers apart. \x00 never occurs in prose, so the placeholders are unambiguous.
const PLACEHOLDER_RE = /\x00(\d+)\x00/g;

function restorePlaceholders(str, maths) {
  return str.replace(PLACEHOLDER_RE, (_, i) => maths[+i]);
}

// Append `str` to `parent`, splitting placeholders back into math text nodes (KaTeX
// consumes them later, wherever they land — including inside <strong>).
function appendTextWithMath(parent, str, maths) {
  let last = 0, m;
  PLACEHOLDER_RE.lastIndex = 0;
  while ((m = PLACEHOLDER_RE.exec(str)) !== null) {
    if (m.index > last) parent.appendChild(document.createTextNode(str.slice(last, m.index)));
    parent.appendChild(document.createTextNode(maths[+m[1]]));   // raw $…$ for KaTeX
    last = m.index + m[0].length;
  }
  if (last < str.length) parent.appendChild(document.createTextNode(str.slice(last)));
}

function makeRef(inner, maths) {
  const pipe = inner.indexOf('|');
  const display = restorePlaceholders((pipe >= 0 ? inner.slice(0, pipe) : inner).trim(), maths);
  const target = (pipe >= 0 ? inner.slice(pipe + 1) : inner).trim();
  const slug = refSlugForRefToken(target);
  if (slug) {
    // notes#72: a real <a href> — not a <span> — so it's natively keyboard-focusable
    // (Tab) and reads as a link to screen readers. bindHoverCards() still intercepts
    // the click to show the preview card instead of navigating immediately; Enter on
    // a focused link fires the same click event, so keyboard and mouse behave alike.
    const a = document.createElement('a');
    a.textContent = display;
    a.href = declHref(slug);
    a.className = 'ref';
    a.setAttribute('data-slug', slug);
    return a;
  }
  const span = document.createElement('span');
  span.textContent = display;
  span.className = 'ref ref-missing';
  span.title = '未解決の参照: ' + target;
  return span;
}

// Inline tokenizer over placeholder-masked text: appends escape-safe DOM nodes
// (text / code / strong / ref) to `parent`; math placeholders are re-expanded on flush.
function tokenizeInline(text, parent, maths) {
  let i = 0, buf = '';
  const n = text.length;
  const flush = () => { if (buf) { appendTextWithMath(parent, buf, maths); buf = ''; } };
  while (i < n) {
    if (text[i] === '[' && text[i + 1] === '[') {
      const close = text.indexOf(']]', i + 2);
      if (close >= 0) { flush(); parent.appendChild(makeRef(text.slice(i + 2, close), maths)); i = close + 2; continue; }
    }
    if (text[i] === '*' && text[i + 1] === '*') {
      const close = text.indexOf('**', i + 2);
      if (close > i + 1) {
        flush();
        const strong = document.createElement('strong');
        tokenizeInline(text.slice(i + 2, close), strong, maths);   // allow math/code/ref inside strong
        parent.appendChild(strong);
        i = close + 2; continue;
      }
    }
    if (text[i] === '`') {
      const close = text.indexOf('`', i + 1);
      if (close >= 0) {
        flush();
        const code = document.createElement('code');
        code.textContent = restorePlaceholders(text.slice(i + 1, close), maths);  // KaTeX ignores <code>
        parent.appendChild(code);
        i = close + 1; continue;
      }
    }
    buf += text[i]; i++;
  }
  flush();
}

// Render one paragraph (math-aware) into `parent` as inline nodes. Math spans are masked
// to placeholders, the residue is inline-tokenized, then placeholders re-expand to math.
function renderParagraph(parent, par) {
  const maths = [];
  let masked = '';
  for (const seg of segmentMath(par)) {
    if (seg.math) { masked += '\x00' + maths.length + '\x00'; maths.push(seg.raw); }
    else masked += joinSoftLines(seg.text);
  }
  tokenizeInline(masked, parent, maths);
}

// Full multi-paragraph prose render (statement_ja / proof_ja / gap.note).
function renderProse(container, text) {
  container.textContent = '';
  for (const par of splitParagraphs(text)) {
    const p = el('p', { class: 'prose-p' });
    renderParagraph(p, par);
    container.appendChild(p);
  }
  typesetMath(container);
}

// Single-line inline render for previews (home cards, hovercards, rows): no <p> wrapper.
function renderProseInline(container, line) {
  container.textContent = '';
  renderParagraph(container, line || '');
  typesetMath(container);
}

// First paragraph, joined to one line (math intact). Used for home-card previews (D1:
// full first paragraph, no truncation).
function firstParagraph(text) {
  const paras = splitParagraphs(text);
  if (!paras.length) return '';
  return segmentMath(paras[0]).map(s => s.math ? s.raw : joinSoftLines(s.text)).join('');
}

// Sentence-boundary preview: within `budget` code points cut at the last 。; if none in
// budget, return the whole first paragraph (D1: semantic boundaries only, never mid-sentence).
function sentencePreview(text, budget) {
  const par = firstParagraph(text);
  const arr = Array.from(par);
  if (arr.length <= budget) return par;
  let cut = -1;
  for (let k = 0; k <= budget && k < arr.length; k++) if (arr[k] === '。') cut = k;
  return cut >= 0 ? arr.slice(0, cut + 1).join('') : par;
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
    + (nodesRes.pin ? ` · leray-hopf @ ${nodesRes.pin.slice(0, 10)}` : '')
    + (nodesRes.has_full_metadata ? '' : ' · (fallback universe: シグネチャ・依存辺なし)');
}

async function loadSources() {
  if (state.sources) return state.sources;
  if (!state.sourcesPromise) {
    const sourcePayload = (state.data && state.data.source_payload) || 'sources.json';
    state.sourcesPromise = fetch('data/' + sourcePayload)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(payload => {
        state.sources = (payload && payload.sources) || {};
        return state.sources;
      })
      .catch(err => {
        state.sourcesPromise = null;
        throw err;
      });
  }
  return state.sourcesPromise;
}

async function loadSourceFor(node) {
  if (node.source) return node.source; // compatibility with older source-embedded payloads
  const sources = await loadSources();
  return sources[node.slug] || null;
}

/* ---------------- routing ---------------- */

/* ---------------- page metadata (notes#73) ----------------
 * route() swaps the contents of <main id="app"> but never touched <head> — every hash
 * route shared the one static <title>/description, so browser tabs, history entries,
 * and bookmark/share UI could not distinguish a declaration page from the site root or
 * from each other. Each render* function below now calls setPageMeta() with a
 * route-specific title/description/canonical.
 *
 * This does NOT by itself make declaration pages independently crawlable by search
 * engines that don't execute JS: the hash fragment is still served by one HTML
 * document, and a <link rel="canonical">/Open Graph tag that only changes via script
 * doesn't create a new indexable URL for such crawlers. Real per-declaration
 * crawlability needs prerendered static routes — tracked as remaining work on #73,
 * not attempted here. */

const SITE_NAME = 'leray-hopf-notes';
const DEFAULT_TITLE = SITE_NAME + ' — 証明掘り下げノート';
const DEFAULT_DESCRIPTION =
  'uda-lab/leray-hopf の全宣言に Lean コードと日本語の数学解説を並置する純静的ビューア。'
  + 'capstone から宣言依存グラフを辿り、直接依存宣言をその場で展開できる。';

// Meta descriptions/OG content must be plain text — statement_ja/doc carry $…$ math,
// **bold**, `code`, and [[display|target]] ref markers meant for renderProseInline's
// DOM-building pipeline, none of which a <meta content="…"> consumer can render.
function stripMarkupForMeta(text) {
  return String(text || '')
    .replace(/\$\$?[^$]*\$\$?/g, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\[\[([^\]|]+)(?:\|[^\]]*)?\]\]/g, '$1')
    .replace(/\s+/g, ' ')
    .replace(/\s+([、。，．])/g, '$1')  // dropped $…$ often leaves "初期値 、" — close the gap
    .trim();
}

function setMetaContent(attr, name, content) {
  let tag = document.querySelector(`meta[${attr}="${name}"]`);
  if (!tag) {
    tag = document.createElement('meta');
    tag.setAttribute(attr, name);
    document.head.appendChild(tag);
  }
  tag.setAttribute('content', content);
}

function setCanonicalLink(href) {
  let link = document.querySelector('link[rel="canonical"]');
  if (!link) {
    link = document.createElement('link');
    link.setAttribute('rel', 'canonical');
    document.head.appendChild(link);
  }
  link.setAttribute('href', href);
}

function setPageMeta(title, description) {
  document.title = title ? `${title} — ${SITE_NAME}` : DEFAULT_TITLE;
  const desc = description || DEFAULT_DESCRIPTION;
  setMetaContent('name', 'description', desc);
  setMetaContent('property', 'og:title', title || DEFAULT_TITLE);
  setMetaContent('property', 'og:description', desc);
  setMetaContent('property', 'og:url', location.href);
  setCanonicalLink(location.href);
}

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
    else if (head === 'proof-status') renderProofStatus(app);
    else if (head === 'about') renderAbout(app, parts[1] ? decodeURIComponent(parts[1]) : null);
    else if (head === 'search') renderSearch(app, decodeURIComponent(parts.slice(1).join('/')));
    else {
      setPageMeta('ページが見つかりません', 'このページは存在しません。');
      app.appendChild(el('p', { text: 'ページが見つかりません。' }));
    }
  } catch (e) {
    // notes#73 (owner review): a thrown decodeURIComponent (malformed %-encoding in the
    // hash, e.g. "#/search/%") or any other renderer exception used to leave the
    // *previous* route's title/description/canonical/OG tags in place — bookmarking or
    // sharing this error page then misrepresented it as the prior page. Reset metadata
    // to a route-agnostic error state before rendering the error itself.
    setPageMeta('レンダリングエラー', 'このページの読み込み中にエラーが発生しました。');
    app.appendChild(el('pre', { class: 'lean', text: 'レンダリングエラー: ' + (e && e.message) }));
    console.error(e);
  }
  window.scrollTo(0, 0);
  // notes#72: <main id="app"> no longer carries a blanket aria-live="polite" (a full
  // page-content swap on every navigation over-announces the entire new DOM to screen
  // readers). Instead, move focus to the new page's own <h1> — the standard SPA a11y
  // pattern — so assistive tech announces just the heading, the same concise signal a
  // sighted user gets from the page visually changing. tabindex="-1" makes an element
  // a valid focus() target without adding it to the normal Tab order.
  const heading = app.querySelector('h1');
  if (heading) {
    heading.setAttribute('tabindex', '-1');
    heading.focus({ preventScroll: true });
  }
}

/* ---------------- home ---------------- */

function renderHome(app) {
  setPageMeta(null, DEFAULT_DESCRIPTION);
  app.appendChild(el('h1', { text: 'Leray–Hopf 形式化 対訳ノート' }));
  app.appendChild(el('p', {
    class: 'prose',
    text: 'uda-lab/leray-hopf の全宣言に Lean コードと日本語の数学解説を並置する純静的ビューア。'
      + 'capstone から宣言依存グラフを辿り、直接依存宣言をその場で展開できる。',
  }));

  // capstone cards
  const grid = el('div', { class: 'capstone-grid' });
  for (const slug of (state.data.capstones || [])) {
    const node = state.bySlug.get(slug);
    if (!node) continue;
    const card = el('div', { class: 'card' }, [
      el('div', { class: 'meta-row' }, [
        node.corpus ? proofStatusBadge(node.corpus.proof_status) : null,
        kindBadge(node.kind),
        gapBadge(node.corpus ? node.corpus.gap.level : 'none'),
      ]),
      el('h3', { text: node.chapter === 'capstone-torus' ? '𝕋³ 主定理' : 'ℝ³ 主定理' }),
      el('a', { class: 'mono', href: declHref(slug), text: node.name }),
    ]);
    if (node.corpus) {
      const p = el('div', { class: 'prose card-preview' });
      renderProseInline(p, firstParagraph(node.corpus.statement_ja));
      card.appendChild(p);
    }
    grid.appendChild(card);
  }
  app.appendChild(grid);

  // coverage mini
  if (state.coverage) {
    const c = state.coverage;
    const wrap = el('div', { class: 'section' }, [el('h3', { text: 'カバレッジ' })]);
    wrap.appendChild(progressBar(c.pct_annotated, `構造的注釈網羅率 ${c.pct_annotated}%`));
    wrap.appendChild(el('p', {
      class: 'filemeta',
      text: `${c.annotated} / ${c.total_decls} 注釈済み (${c.pct_annotated}%) · full ${c.full} · gloss ${c.gloss}`,
    }));
    wrap.appendChild(el('p', { class: 'caveat' }, [
      el('strong', { text: '注意：' }),
      el('span', { text: 'この 100% は「構造的注釈網羅率」（statement_ja 等の記入率）であり、証明の完成度や数学的検証を意味しない。' }),
    ]));
    const nv = c.not_verified || 0;
    if (nv) {
      wrap.appendChild(el('p', { class: 'filemeta' }, [
        el('a', { href: '#/proof-status', text: `証明状態が verified でない宣言: ${nv} 件 →` }),
      ]));
    }
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

function progressBar(pct, label) {
  const clamped = Math.max(0, Math.min(100, pct));
  // notes#72: role="progressbar" + aria-value* so screen readers announce the actual
  // percentage, not just an unlabeled colored bar. The fill width is set as a JS
  // CSSOM property (el.style.width = …), not via an HTML style="" attribute — the
  // el() helper's `style:` key would setAttribute('style', …), which a CSP
  // `style-src 'self'` (no 'unsafe-inline') would block; property assignment is not
  // restricted by CSP.
  const bar = el('div', {
    class: 'progress', role: 'progressbar',
    'aria-valuenow': String(clamped), 'aria-valuemin': '0', 'aria-valuemax': '100',
    'aria-label': label || `${clamped}%`,
  });
  const fill = el('span');
  fill.style.width = clamped + '%';
  bar.appendChild(fill);
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
  if (!node) {
    setPageMeta('宣言が見つかりません', `"${slug}" という宣言は見つかりませんでした。`);
    app.appendChild(el('p', { text: '宣言が見つかりません: ' + slug }));
    return;
  }
  const rawDesc = (node.corpus && node.corpus.statement_ja) ? node.corpus.statement_ja : node.doc;
  setPageMeta(node.name, rawDesc ? stripMarkupForMeta(sentencePreview(rawDesc, META_DESCRIPTION_BUDGET)) : null);
  updateTrail(slug);

  app.appendChild(breadcrumb(node));

  const title = el('h1', { class: 'decl-title' }, [el('span', { class: 'short', text: node.shortName })]);
  app.appendChild(title);

  const hasNote = !!(node.corpus && node.corpus.gap && node.corpus.gap.note);
  const gapEl = node.corpus ? gapBadge(node.corpus.gap.level) : null;
  if (gapEl && hasNote) {
    // Header gap badge scroll-links to the Note (relocated below the proof band, D4).
    gapEl.classList.add('gap-link');
    gapEl.setAttribute('role', 'link');
    gapEl.setAttribute('tabindex', '0');
    const jump = () => scrollIntoViewSafe(document.getElementById('gap-note'));
    gapEl.addEventListener('click', jump);
    gapEl.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); jump(); } });
  }
  const proofStatus = node.corpus ? node.corpus.proof_status : null;
  const meta = el('div', { class: 'meta-row' }, [
    proofStatusBadge(proofStatus),
    kindBadge(node.kind),
    gapEl,
    node.corpus ? tierBadge(node.corpus.tier) : badge('tier-gloss', '未注釈'),
    node.private ? badge('priv', 'private') : null,
    node.corpus && node.corpus.sample ? badge('sample', 'sample') : null,
  ]);
  const chMeta = state.chapterMeta.get(node.chapter);
  meta.appendChild(el('a', { class: 'badge', href: chapterHref(node.chapter), text: (chMeta && chMeta.label_ja) || node.chapter }));
  app.appendChild(meta);
  app.appendChild(el('p', { class: 'mono filemeta' }, [
    node.name + '  ·  ',
    fileLineNode('filemeta', node.file, node.startLine, node.startLine),
  ]));
  // notes#65: prominent banner right under the header — a sorry-carrying / scaffold /
  // retired / quarantined declaration must not read like an ordinary proved theorem.
  const banner = proofStatusBanner(proofStatus);
  if (banner) app.appendChild(banner);

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
    if (node.has_source) {
      const srcLink = fileLineNode('filemeta', node.file, node.startLine, node.endLine);
      if (srcLink.tagName === 'A') srcLink.addEventListener('click', ev => ev.stopPropagation());
      det.appendChild(el('summary', {}, [
        el('span', { class: 'summary-name', text: 'ソースを表示' }),
        srcLink,
      ]));
      const wrap = el('div', { class: 'codewrap' });
      const placeholder = el('p', { class: 'filemeta', text: 'ソース本文を取得しています。' });
      wrap.appendChild(placeholder);
      inner.appendChild(wrap);
      let loaded = false;
      det.addEventListener('toggle', () => {
        if (!det.open || loaded) return;
        loaded = true;
        loadSourceFor(node).then(src => {
          wrap.innerHTML = '';
          if (src) {
            wrap.appendChild(el('pre', { class: 'lean source', html: highlightLean(src) }));
          } else {
            wrap.appendChild(el('p', {
              class: 'filemeta',
              text: `ソース本文が見つかりません。位置: ${node.file}:${node.startLine}–${node.endLine}`,
            }));
          }
        }).catch(() => {
          loaded = false;
          wrap.innerHTML = '';
          wrap.appendChild(el('p', {
            class: 'filemeta',
            text: `ソース payload を読み込めませんでした。パネルを閉じて再度開くと再試行します。位置: ${node.file}:${node.startLine}–${node.endLine}`,
          }));
        });
      });
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

  // Formalization-gap Note — relocated below the proof band (D4). Shown whenever a note
  // exists (mild or large); the header gap badge scroll-links here.
  if (hasNote) {
    const np = el('div', { class: 'note-panel', id: 'gap-note' }, [
      el('h4', { text: '形式化ギャップ (Note)' }),
    ]);
    const body = el('div', { class: 'prose' });
    renderProse(body, node.corpus.gap.note);
    np.appendChild(body);
    app.appendChild(np);
  }

  // notes#68: bibliographic citations backing this declaration's statement/proof/naming
  // choices, resolved from state.data.bibliography (built from docs/bibliography.md).
  const refs = node.corpus && node.corpus.references;
  if (refs && refs.length) {
    const rp = el('div', { class: 'note-panel refs-panel' }, [
      el('h4', { text: '参考文献' }),
    ]);
    const list = el('ul', { class: 'refs-list' });
    for (const ref of refs) {
      const citation = (state.data.bibliography || {})[ref.id];
      const li = el('li', {}, [
        el('a', { href: '#/about/' + encodeURIComponent(ref.id), class: 'mono', text: ref.id }),
        ref.locator ? el('span', { class: 'filemeta', text: ' ' + ref.locator }) : null,
        el('span', { class: 'ref-citation', text: citation ? '  ' + citation : '  (未解決の citation id)' }),
      ]);
      list.appendChild(li);
    }
    rp.appendChild(list);
    app.appendChild(rp);
  }

  // notes#69: development-process history (issue/PR numbers, review rounds, axiom-to-theorem
  // flips, module reorganizations) is kept for the historical record but must not lead the
  // default scholarly view — collapsed behind a <details> toggle, closed by default, below
  // the mathematical content (statement/proof/gap-note/references).
  const provenance = node.corpus && node.corpus.provenance;
  if (provenance) {
    const pp = el('div', { class: 'note-panel provenance-panel' });
    const det = el('details', { class: 'use' });
    det.appendChild(el('summary', {}, [el('span', { class: 'summary-name', text: '開発履歴を表示' })]));
    const body = el('div', { class: 'prose use-body' });
    renderProse(body, provenance);
    det.appendChild(body);
    pp.appendChild(det);
    app.appendChild(pp);
  }

  // uses (direct deps) — depth-1 accordion
  renderUses(app, node);
  // used-by (links only)
  renderUsedBy(app, node);
}

function leanPane(label, code, node) {
  const pane = el('div', { class: 'pane lean' });
  pane.appendChild(el('h4', { text: label }));
  const wrap = el('div', { class: 'codewrap' });
  const pre = el('pre', { class: 'lean', html: highlightLean(code) });
  wrap.appendChild(pre);
  pane.appendChild(wrap);
  if (node) pane.appendChild(el('div', { class: 'filemeta-block' }, [fileLineNode('filemeta', node.file, node.startLine, node.startLine)]));
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
  const sec = el('div', { class: 'section' }, [el('h3', { text: `直接依存宣言 uses (${node.uses.length})` })]);
  if (!node.uses.length) sec.appendChild(el('p', { class: 'filemeta', text: '直接依存なし。' }));
  for (const slug of node.uses) {
    const dep = state.bySlug.get(slug);
    if (!dep) continue;
    const det = el('details', { class: 'use' });
    const summary = el('summary', {}, [
      kindBadge(dep.kind),
      el('span', { class: 'summary-name', text: dep.shortName }),
      dep.corpus ? proofStatusBadge(dep.corpus.proof_status) : null,
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
  // "no usedBy" means no other extracted declaration references this one — it says nothing
  // about this node's own `uses` (which may be nonempty), so "葉/leaf" (no outgoing edges)
  // is the wrong term here; only describe the incoming-edge fact.
  if (!node.usedBy.length) { sec.appendChild(el('p', { class: 'filemeta', text: 'このノードを直接使う宣言はありません（capstone であるか、抽出対象の中では他のどこからも参照されていません）。' })); app.appendChild(sec); return; }
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
  setPageMeta(
    (chMeta && chMeta.label_ja) || chId,
    (chMeta && chMeta.description) ? stripMarkupForMeta(chMeta.description) : null);
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
  const psBadge = n.corpus ? proofStatusBadge(n.corpus.proof_status) : null;
  if (psBadge) row.appendChild(psBadge);
  if (n.corpus) {
    const one = el('span', { class: 'one-line' });
    renderProseInline(one, sentencePreview(n.corpus.statement_ja, ROW_PREVIEW_BUDGET));
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
  setPageMeta('宣言依存グラフ', '2 つの capstone を根に、直接依存宣言 (uses) を段階的に展開して辿れる宣言依存グラフ。');
  app.appendChild(el('h1', { text: '宣言依存グラフ (DAG)' }));
  const total = (state.data && state.data.decl_count) || 0;
  app.appendChild(el('p', {
    class: 'prose',
    text: '2 つの capstone を根に、直接依存宣言 (uses) をクリックで段階的に展開する。'
      + `全 ${total.toLocaleString('ja-JP')} 宣言を一度には描画しない（段階的開示のみ）。`,
  }));
  const container = el('div', { class: 'dag' });
  const rootUl = el('ul');
  for (const slug of (state.data.capstones || [])) {
    const node = state.bySlug.get(slug);
    if (node) rootUl.appendChild(dagItem(node, new Set([slug])));
  }
  container.appendChild(rootUl);
  app.appendChild(container);
}

function dagItem(node, ancestors) {
  const li = el('li');
  const hasChildren = node.uses.length > 0;
  // notes#72: the expand/collapse control must be a real keyboard-operable control
  // (Tab to focus, Enter/Space to activate — native <button> behavior) with
  // aria-expanded reflecting state, not a clickable <span>. The leaf marker has no
  // interaction, so it stays a decorative <span aria-hidden>.
  const twist = hasChildren
    ? el('button', {
        type: 'button', class: 'twist', text: '▸',
        'aria-expanded': 'false',
        'aria-label': `${node.shortName} の依存を展開`,
      })
    : el('span', { class: 'twist leaf', text: '·', 'aria-hidden': 'true' });
  const row = el('div', { class: 'node-row' }, [
    twist,
    kindBadge(node.kind),
    el('a', { class: 'dag-name', href: declHref(node.slug), text: node.shortName }),
    node.corpus ? proofStatusBadge(node.corpus.proof_status) : null,
    node.corpus ? gapBadge(node.corpus.gap.level) : null,
    badge('annotated', node.corpus ? '注釈済' : '—'),
  ]);
  li.appendChild(row);

  if (hasChildren) {
    let childUl = null;
    twist.addEventListener('click', () => {
      if (childUl) {
        const open = childUl.style.display !== 'none';
        childUl.style.display = open ? 'none' : '';
        twist.textContent = open ? '▸' : '▾';
        twist.setAttribute('aria-expanded', open ? 'false' : 'true');
        return;
      }
      childUl = el('ul');
      for (const slug of node.uses) {
        const child = state.bySlug.get(slug);
        if (!child) continue;
        if (ancestors.has(slug)) { // avoid cycle re-expansion in this branch
          childUl.appendChild(el('li', {}, [el('div', { class: 'node-row' }, [
            el('span', { class: 'twist leaf', text: '↻', 'aria-hidden': 'true' }),
            el('a', { class: 'dag-name', href: declHref(slug), text: child.shortName }),
          ])]));
          continue;
        }
        const next = new Set(ancestors); next.add(slug);
        childUl.appendChild(dagItem(child, next));
      }
      li.appendChild(childUl);
      twist.textContent = '▾';
      twist.setAttribute('aria-expanded', 'true');
    });
  }
  return li;
}

/* ---------------- coverage page ---------------- */

function renderCoverage(app) {
  const c = state.coverage;
  setPageMeta('カバレッジ', c
    ? `構造的注釈網羅率 ${c.pct_annotated}%（${c.annotated} / ${c.total_decls} 宣言）の章別カバレッジ一覧。`
    : null);
  app.appendChild(el('h1', { text: 'カバレッジ' }));
  if (!c) { app.appendChild(el('p', { text: 'coverage.json を読み込めませんでした。' })); return; }
  app.appendChild(progressBar(c.pct_annotated, `構造的注釈網羅率 ${c.pct_annotated}%`));
  app.appendChild(el('p', { class: 'filemeta', text: `全体: ${c.annotated} / ${c.total_decls} (${c.pct_annotated}%) · full ${c.full} · gloss ${c.gloss}` }));
  app.appendChild(el('p', { class: 'caveat' }, [
    el('strong', { text: '注意：' }),
    el('span', {
      text: 'ここでの割合は「構造的注釈網羅率」（各宣言に statement_ja 等が記入されている割合）である。'
        + '証明の完成度・数学的な検証状態を意味しない。「tier: full」も解説の詳しさを表すのみで、証明済みの保証ではない。'
        + '個々の宣言の証明状態（sorry・足場・廃止・隔離中）は下のリンク、または各宣言ページのバッジで確認できる。',
    }),
  ]));
  if (c.proof_status_counts) {
    const nv = c.not_verified || 0;
    app.appendChild(el('p', {}, [
      el('a', { href: '#/proof-status', text: `証明状態の一覧を見る（verified でない宣言: ${nv} 件） →` }),
    ]));
  }

  // notes#72: <caption>/<thead>/<tbody> + scope so the table structure is announced
  // correctly by screen readers, not just visually implied by row order.
  const table = el('table', { class: 'coverage' });
  table.appendChild(el('caption', { text: '章別の構造的注釈網羅率' }));
  const thead = el('thead');
  thead.appendChild(el('tr', {}, [
    el('th', { scope: 'col', text: '章' }), el('th', { scope: 'col', class: 'num', text: '総数' }),
    el('th', { scope: 'col', class: 'num', text: '注釈済' }), el('th', { scope: 'col', class: 'num', text: 'full' }),
    el('th', { scope: 'col', class: 'num', text: 'gloss' }), el('th', { scope: 'col', class: 'num', text: '%' }),
  ]));
  table.appendChild(thead);
  const tbody = el('tbody');
  for (const ch of (state.data.chapters || [])) {
    const stat = (c.chapters && c.chapters[ch.id]) || { annotated: 0, full: 0, gloss: 0 };
    const total = state.chapterTotals.get(ch.id) || 0;
    const pct = total ? Math.round(1000 * stat.annotated / total) / 10 : 0;
    tbody.appendChild(el('tr', {}, [
      el('th', { scope: 'row' }, [el('a', { href: chapterHref(ch.id), text: ch.label_ja || ch.id })]),
      el('td', { class: 'num', text: String(total) }),
      el('td', { class: 'num', text: String(stat.annotated) }),
      el('td', { class: 'num', text: String(stat.full) }),
      el('td', { class: 'num', text: String(stat.gloss) }),
      el('td', { class: 'num', text: pct + '%' }),
    ]));
  }
  table.appendChild(tbody);
  app.appendChild(table);
}

/* ---------------- proof-status page (notes#65) ----------------
 * Enumerates every declaration whose corpus.proof_status is not the default 'verified',
 * grouped by status. Sourced directly from nodes.json (built deterministically by
 * scripts/build_site_data.py from the corpus at the pinned leray-hopf SHA), so this list is
 * mechanically derived from — and always matches — the site data, not hand-curated prose. */

const PROOF_STATUS_ORDER = ['contains-sorry', 'invalid-statement', 'scaffold', 'retired'];

function renderProofStatus(app) {
  setPageMeta('証明状態（proof_status）一覧', 'sorry・足場・撤去済みなど、verified 以外の証明状態をもつ宣言の一覧。');
  app.appendChild(el('div', { class: 'breadcrumb' }, [
    el('a', { href: '#/', text: 'ホーム' }), el('span', { class: 'sep', text: '›' }),
    el('span', { text: '証明状態' }),
  ]));
  app.appendChild(el('h1', { text: '証明状態（proof_status）一覧' }));
  app.appendChild(el('p', {
    class: 'prose',
    text: '`tier`（注釈の詳しさ）とは独立に、各宣言の証明としての完成度を示す。'
      + '一覧にない宣言はすべて既定値 verified（既知の sorry・虚偽/過度な一般化・歴史的足場・廃止のいずれにも該当しない）である。'
      + (state.data && state.data.pin ? ` 集計対象: leray-hopf @ ${state.data.pin.slice(0, 10)}。` : ''),
  }));

  const legend = el('div', { class: 'section' }, [el('h3', { text: '凡例' })]);
  const dl = el('div', { class: 'proof-status-legend' });
  for (const status of PROOF_STATUS_ORDER) {
    const meta = PROOF_STATUS_META[status];
    dl.appendChild(el('div', { class: 'legend-row' }, [proofStatusBadge(status), el('span', { text: meta.desc })]));
  }
  legend.appendChild(dl);
  app.appendChild(legend);

  const byStatus = new Map();
  for (const n of state.data.nodes) {
    const status = n.corpus && n.corpus.proof_status;
    if (status && status !== 'verified') {
      if (!byStatus.has(status)) byStatus.set(status, []);
      byStatus.get(status).push(n);
    }
  }

  for (const status of PROOF_STATUS_ORDER) {
    const nodes = (byStatus.get(status) || []).sort(byName);
    const meta = PROOF_STATUS_META[status];
    const sec = el('div', { class: 'section' }, [
      el('h3', {}, [proofStatusBadge(status), el('span', { text: ` — ${nodes.length} 件` })]),
    ]);
    if (!nodes.length) sec.appendChild(el('p', { class: 'filemeta', text: '該当なし。' }));
    for (const n of nodes) sec.appendChild(declRow(n));
    app.appendChild(sec);
  }
}

/* ---------------- about / citation / bibliography (notes#68) ---------------- */

function renderAbout(app, highlightId) {
  const citation = state.data.citation || {};
  const pin = state.data.pin;
  const bib = state.data.bibliography || {};

  setPageMeta('このサイトについて', 'author・scope・citation・license・参考文献一覧・disclaimer。');
  app.appendChild(el('h1', { text: 'このサイトについて' }));

  const scope = el('div', { class: 'section' }, [
    el('h3', { text: 'author・scope' }),
    el('p', { class: 'prose' }, [
      (citation.authors && citation.authors.length ? citation.authors.join(', ') : '(author 未設定)')
        + ' による、',
      el('a', { href: 'https://github.com/uda-lab/leray-hopf', text: 'uda-lab/leray-hopf' }),
      ' （Leray–Hopf 弱解存在の Lean 4 + mathlib 形式化）の全宣言対訳解説サイト。'
        + 'corpus/**/*.yaml のprose と Lean 宣言メタデータを結合した純静的ビューア。',
    ]),
  ]);
  app.appendChild(scope);

  const disclaimer = el('div', { class: 'section' }, [
    el('h3', { text: '注意（disclaimer）' }),
    el('p', { class: 'caveat' }, [
      el('strong', { text: '注意：' }),
      el('span', {
        text: 'このサイトが示す「注釈網羅率」「proof_status: verified」は、宣言に'
          + ' statement_ja 等が記入され Lean 側に既知の sorry・虚偽/過度に一般化された主張・'
          + '撤去済み宣言としてのマークがないことを意味するのみであり、対訳注釈そのものが'
          + '数学的に正しいことを証明・認証するものではない（semantic proof certification'
          + ' ではない）。証明の真の正しさの根拠は Lean 側の型検査そのものであり、この'
          + 'サイトの日本語注釈は理解のための補助である。',
      }),
    ]),
    el('p', {}, [el('a', { href: '#/proof-status', text: '証明状態の内訳を見る →' })]),
  ]);
  app.appendChild(disclaimer);

  const citeSec = el('div', { class: 'section' }, [el('h3', { text: 'citation・license' })]);
  const citeList = el('ul', { class: 'about-list' });
  if (citation.repository_code) {
    citeList.appendChild(el('li', {}, [
      'このリポジトリ: ',
      el('a', { href: citation.repository_code, text: citation.repository_code }),
      ' — ',
      el('a', { href: citation.repository_code + '/blob/main/CITATION.cff', text: 'CITATION.cff' }),
    ]));
  }
  if (citation.source_repository) {
    const commitHref = pin ? `${citation.source_repository}/tree/${pin}` : citation.source_repository;
    citeList.appendChild(el('li', {}, [
      '形式化ソース: ',
      el('a', { href: citation.source_repository, text: citation.source_repository }),
      pin ? el('span', {}, [' — pinned commit ', el('a', { class: 'mono', href: commitHref, text: pin })]) : null,
    ]));
  }
  if (citation.license) {
    citeList.appendChild(el('li', { text: 'license: ' + [].concat(citation.license).join(', ')
      + '（ファイル別の適用範囲は LICENSE.md を参照。vendored KaTeX は MIT）' }));
    if (citation.license_url) {
      citeList.appendChild(el('li', {}, [el('a', { href: citation.license_url, text: 'LICENSE.md' })]));
    }
  }
  if (state.data.built_at) {
    citeList.appendChild(el('li', { text: `このサイトデータのビルド日時: ${state.data.built_at}` }));
  }
  citeSec.appendChild(citeList);
  app.appendChild(citeSec);

  const bibSec = el('div', { class: 'section' }, [
    el('h3', { text: '参考文献 (bibliography)' }),
    el('p', { class: 'filemeta', text: 'corpus の宣言注釈が略記で引く一次・標準文献。個々の宣言からのリンクは各宣言ページの「参考文献」欄を参照。' }),
  ]);
  const bibList = el('ul', { class: 'refs-list' });
  for (const cid of Object.keys(bib).sort()) {
    const li = el('li', { id: 'ref-' + cid }, [
      el('span', { class: 'mono', text: cid }),
      el('span', { class: 'ref-citation', text: '  ' + bib[cid] }),
    ]);
    if (cid === highlightId) li.classList.add('ref-highlight');
    bibList.appendChild(li);
  }
  bibSec.appendChild(bibList);
  app.appendChild(bibSec);

  if (highlightId) {
    setTimeout(() => scrollIntoViewSafe(document.getElementById('ref-' + highlightId)), 0);
  }
}

/* ---------------- search ---------------- */

function renderSearch(app, q) {
  const input = document.getElementById('search-input');
  if (input && input.value !== q) input.value = q;
  q = (q || '').trim();
  setPageMeta(q ? `検索: ${q}` : '検索', q ? null : '宣言名・statement・proof・tags を対象に検索する。');
  app.appendChild(el('h1', { text: '検索' }));
  if (!q) { app.appendChild(el('p', { class: 'filemeta', text: '検索語を入力してください。' })); return; }

  const ql = q.toLowerCase();
  const hits = [];
  // notes#73: previously name + statement_ja only ("Possible work" in #73 called out
  // proof/tags as under-covered) — widened to also match corpus.tags and proof_ja, plus
  // the raw Lean docstring. notes#73 (owner review): statement_ja/proof_ja must also
  // compare case-insensitively like every other field here — English terms embedded in
  // the Japanese prose (e.g. "Galerkin") were only matching an exact-case query otherwise.
  for (const n of state.data.nodes) {
    const nameHit = n.name.toLowerCase().includes(ql) || n.shortName.toLowerCase().startsWith(ql);
    const stmtHit = n.corpus && n.corpus.statement_ja && n.corpus.statement_ja.toLowerCase().includes(ql);
    const proofHit = n.corpus && n.corpus.proof_ja && n.corpus.proof_ja.toLowerCase().includes(ql);
    const tagHit = n.corpus && Array.isArray(n.corpus.tags) && n.corpus.tags.some(t => t.toLowerCase().includes(ql));
    const docHit = n.doc && n.doc.toLowerCase().includes(ql);
    if (nameHit || stmtHit || proofHit || tagHit || docHit) hits.push(n);
  }
  // notes#73 (codex pre-review): setPageMeta() above ran before hits were counted, so it
  // left og:description at DEFAULT_DESCRIPTION for any non-empty query — update both the
  // plain meta description and og:description together now that the count is known.
  const resultDesc = `"${q}" の検索結果 ${hits.length} 件。`;
  setMetaContent('name', 'description', resultDesc);
  setMetaContent('property', 'og:description', resultDesc);
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
let hoverBound = false;
let activeRefEl = null;   // notes#72: last ref that opened the card, for Escape-to-return-focus

/* Bind hover/tap on `.ref` spans once, on the document, via event delegation. Refs now
 * appear both in Lean code (highlightLean) and in Japanese prose ([[…]] tokens, D5), on
 * every page — a single delegated binding covers them all and avoids the duplicate
 * listeners the old per-render binding accumulated on the persistent #app element. */
function bindHoverCards() {
  if (hoverBound) return;
  hoverBound = true;
  document.addEventListener('mouseover', ev => {
    const t = ev.target.closest && ev.target.closest('.ref[data-slug]');
    if (t) showHoverCard(t);
  });
  document.addEventListener('mouseout', ev => {
    const t = ev.target.closest && ev.target.closest('.ref[data-slug]');
    if (t) hoverTimer = setTimeout(hideHoverCard, 180);
  });
  document.addEventListener('click', ev => {
    const t = ev.target.closest && ev.target.closest('.ref[data-slug]');
    if (!t) return;
    // notes#72: a real mouse/touch click (MouseEvent.detail >= 1) shows the pinned
    // preview instead of jumping, as before. But Enter on a focused <a> also fires a
    // synthetic click with detail === 0 — and the pinned card's own "open" link isn't
    // reliably the next Tab stop (the card lives at the end of <body>, not next to the
    // ref, in DOM/tab order), so intercepting that click too left keyboard users with
    // no way to actually follow the reference (caught in codex review). Let
    // keyboard-triggered activation navigate normally instead.
    if (ev.detail === 0) return;
    ev.preventDefault();          // touch / tap: show the card instead of jumping
    showHoverCard(t, true);
  });
  // notes#72: keyboard equivalent of hover — focusin shows the same preview Tab-ing
  // through prose that mouseover shows while pointing at it; Enter then navigates
  // directly (see the click handler's ev.detail check above), matching plain <a>
  // behavior rather than requiring an extra step to reach the card's own link.
  document.addEventListener('focusin', ev => {
    const t = ev.target.closest && ev.target.closest('.ref[data-slug]');
    if (t) showHoverCard(t, true);
  });
  document.addEventListener('focusout', ev => {
    const t = ev.target.closest && ev.target.closest('.ref[data-slug]');
    if (!t) return;
    const next = ev.relatedTarget;
    const card = document.getElementById('hovercard');
    if (next && card && card.contains(next)) return; // focus moved into the card itself
    hoverTimer = setTimeout(hideHoverCard, 180);
  });
  // Escape dismisses the card and returns focus to whatever ref opened it, so keyboard
  // users are never left with a visible popover and no way to close it without a mouse.
  document.addEventListener('keydown', ev => {
    if (ev.key !== 'Escape') return;
    const card = document.getElementById('hovercard');
    if (!card || card.hidden) return;
    hideHoverCard();
    if (activeRefEl) activeRefEl.focus();
  });
}

function showHoverCard(refEl, pin) {
  clearTimeout(hoverTimer);
  const slug = refEl.getAttribute('data-slug');
  const node = state.bySlug.get(slug);
  if (!node) return;
  activeRefEl = refEl;
  const card = document.getElementById('hovercard');
  card.innerHTML = '';
  card.appendChild(el('div', { class: 'meta-row' }, [
    node.corpus ? proofStatusBadge(node.corpus.proof_status) : null,
    kindBadge(node.kind),
    node.corpus ? gapBadge(node.corpus.gap.level) : null,
  ]));
  const sigLine = (node.signature || '').split('\n').find(l => l.trim()) || node.name;
  card.appendChild(el('div', { class: 'hc-sig', text: sigLine }));
  if (node.corpus && node.corpus.statement_ja) {
    const s = el('div', { class: 'hc-stmt' });
    renderProseInline(s, sentencePreview(node.corpus.statement_ja, HOVER_PREVIEW_BUDGET));
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

// notes#72: the skip link's `href="#app"` must NOT be left to native fragment
// navigation — every hash change fires the `hashchange` listener below, and route()
// treats any hash that isn't one of its known routes (all of which start with `#/`) as
// "page not found". #app matches nothing, so without this handler, activating the skip
// link would replace the current page with a not-found view instead of just moving
// focus past the header. preventDefault() keeps location.hash untouched entirely.
function setupSkipLink() {
  const link = document.querySelector('.skip-link');
  const app = document.getElementById('app');
  if (!link || !app) return;
  link.addEventListener('click', ev => {
    ev.preventDefault();
    app.focus();
  });
}

async function boot() {
  setupSearch();
  setupSkipLink();
  bindHoverCards();
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

const IS_NODE_MODULE = typeof module !== 'undefined' && module.exports;
if (typeof document !== 'undefined' && !IS_NODE_MODULE) {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
}

/* Test shim (notes#12 jsdom harness): expose pure renderers under Node without affecting
 * the browser path. No-op in the browser (module is undefined). */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    state, splitParagraphs, joinSoftLines, joinGlue, segmentMath, tokenizeInline,
    makeRef, refSlugForRefToken, renderParagraph, renderProse, renderProseInline,
    firstParagraph, sentencePreview, renderDecl, renderAbout, loadSources, loadSourceFor,
    proofStatusBadge, proofStatusBanner, renderProofStatus, PROOF_STATUS_META,
    renderDag, renderUsedBy, renderUses,
    esc, dagItem, progressBar, renderCoverage, route,
    bindHoverCards, setupSkipLink,
    setPageMeta, stripMarkupForMeta, DEFAULT_TITLE, DEFAULT_DESCRIPTION,
  };
}
