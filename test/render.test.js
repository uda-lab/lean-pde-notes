'use strict';
/* jsdom render harness for site/app.js (notes#12 §受け入れ基準).
 *
 * Loads the browser SPA under jsdom (the module.exports shim in app.js exposes the pure
 * renderers and suppresses auto-boot), stubs a fixture `state`, and asserts the D1/D4/D5
 * acceptance criteria at the DOM level. No network, no KaTeX (renderMathInElement is left
 * undefined so math text nodes survive verbatim, exactly as KaTeX would consume them). */

const assert = require('assert');
const { JSDOM } = require('jsdom');

const dom = new JSDOM(
  '<!DOCTYPE html><body><main id="app"></main><div id="hovercard" hidden></div></body>',
  { url: 'http://localhost/' });
global.window = dom.window;
global.document = dom.window.document;
global.location = dom.window.location; // route() (notes#72 test (n)) reads bare `location`
// notes#73 (codex pre-review): jsdom doesn't implement window.scrollTo — route() calls
// it unconditionally on every navigation, which otherwise logs a noisy (non-fatal)
// "Not implemented" error on every route()-driven check in this file.
dom.window.scrollTo = () => {};

const app = require('../site/app.js');
const {
  state, splitParagraphs, joinSoftLines, firstParagraph, sentencePreview,
  renderProse, renderProseInline, renderDecl, renderAbout, loadSourceFor,
  proofStatusBadge, proofStatusBanner, renderDag, renderUsedBy,
  esc, dagItem, progressBar, renderCoverage, route, makeRef,
  bindHoverCards, setupSkipLink,
  setPageMeta, stripMarkupForMeta, DEFAULT_TITLE, DEFAULT_DESCRIPTION,
} = app;

let passed = 0;
const pending = [];
function check(name, fn) {
  const result = fn();
  const done = () => {
    passed += 1;
    console.log(`  ok  ${name}`);
  };
  if (result && typeof result.then === 'function') pending.push(result.then(done));
  else done();
}

/* ---- fixture universe ---- */
function addNode(n) {
  state.bySlug.set(n.slug, n);
  state.nameDict.set(n.name, n.slug);
  state.shortDict.set(n.shortName, n.slug);
}
addNode({
  slug: 'LerayHopf.lerayProjection', id: 'LerayHopf.lerayProjection',
  name: 'LerayHopf.lerayProjection', shortName: 'lerayProjection', kind: 'def',
  signature: 'def lerayProjection', file: 'Leray.lean', startLine: 1, endLine: 1,
  chapter: 'spaces', uses: [], usedBy: [], private: false, corpus: null,
});
// notes#73: fixture with statement_ja/proof_ja/tags/doc for page-metadata + widened-search tests.
addNode({
  slug: 'LerayHopf.weakSolutionExists', id: 'LerayHopf.weakSolutionExists',
  name: 'LerayHopf.weakSolutionExists', shortName: 'weakSolutionExists', kind: 'theorem',
  signature: 'theorem weakSolutionExists', file: 'Existence.lean', startLine: 10, endLine: 20,
  chapter: 'existence', uses: [], usedBy: [], private: false,
  doc: 'Existence of a Leray-Hopf weak solution.',
  corpus: {
    statement_ja: '発散ゼロな初期値 $u_0$ に対し **Leray–Hopf 弱解** が存在する。すなわちエネルギー不等式を満たす。',
    proof_ja: 'Galerkin 近似で構成する。',
    tags: ['existence-uniqueness'],
    gap: { level: 'none' },
    proof_status: 'verified', tier: 'full',
  },
});

/* ==== 受け入れ基準 1: home capstone card — untruncated first paragraph ==== */
check('(a) capstone first paragraph is untruncated (no すなわち cut-off)', () => {
  const statement =
    '発散ゼロな初期値 $u_0$、粘性 $\\nu>0$、時刻 $T>0$ に対して、Navier–Stokes 方程式は Leray–Hopf 弱解をもつ。\n\n' +
    'すなわち、エネルギー不等式を満たす曲線 $u$ が存在する。';
  const fp = firstParagraph(statement);
  assert.ok(fp.endsWith('。'), 'first paragraph should end at a sentence boundary');
  assert.ok(fp.includes('弱解をもつ'), 'first paragraph must retain its final clause');
  assert.ok(!fp.includes('すなわち'), 'first paragraph must not bleed into paragraph 2');

  const card = document.createElement('div');
  renderProseInline(card, fp);
  assert.ok(card.textContent.includes('弱解をもつ。'), 'card renders the full first paragraph');
  assert.ok(!card.textContent.includes('…'), 'no ellipsis / char-count truncation');
});

/* ==== 受け入れ基準 3 + 4: inline tokens render; no raw markup leaks ==== */
check('(b) [[…]] ref renders as a hover-ref span with resolved data-slug', () => {
  const div = document.createElement('div');
  renderProse(div, 'ここで [[Leray 射影|LerayHopf.lerayProjection]] を用いる。');
  const ref = div.querySelector('.ref[data-slug]');
  assert.ok(ref, 'a .ref[data-slug] span must exist');
  assert.strictEqual(ref.textContent, 'Leray 射影');
  assert.strictEqual(ref.getAttribute('data-slug'), 'LerayHopf.lerayProjection');
});

check('(c) no raw ** / backtick / [[ remain after rendering', () => {
  const div = document.createElement('div');
  renderProse(div, 'これは **強調** と `コード` と [[Leray 射影|LerayHopf.lerayProjection]] を含む。');
  assert.strictEqual(div.querySelector('strong').textContent, '強調');
  assert.strictEqual(div.querySelector('code').textContent, 'コード');
  const txt = div.textContent;
  assert.ok(!txt.includes('**'), 'no raw ** in rendered prose');
  assert.ok(!txt.includes('`'), 'no raw backtick in rendered prose');
  assert.ok(!txt.includes('[['), 'no raw [[ in rendered prose');
});

check('unresolved [[…]] ref still consumes the brackets (renders ref-missing)', () => {
  const div = document.createElement('div');
  renderProse(div, '[[未知の語|LerayHopf.doesNotExist]] を参照。');
  const miss = div.querySelector('.ref-missing');
  assert.ok(miss, 'unresolved ref renders as .ref-missing');
  assert.strictEqual(miss.textContent, '未知の語');
  assert.ok(!div.textContent.includes('[['), 'brackets consumed even when unresolved');
});

check('(c-regression) **strong** enclosing a $…$ span does not leak raw **', () => {
  const div = document.createElement('div');
  renderProse(div, '速度場 $u$ の **$H^1$ エネルギー二乗** を定める。');
  const strong = div.querySelector('strong');
  assert.ok(strong, 'a <strong> must be produced even though it wraps math');
  assert.ok(strong.textContent.includes('$H^1$'), 'math inside strong is kept verbatim for KaTeX');
  assert.ok(!div.textContent.includes('**'), 'no raw ** leaks when strong spans a math boundary');
});

check('math segments are preserved verbatim for KaTeX (tokenizer does not touch $…$)', () => {
  const div = document.createElement('div');
  renderProse(div, '式 $a_{**}$ の外で **強調**。');
  // ** inside math is NOT a strong marker; only the outer ** is.
  assert.strictEqual(div.querySelectorAll('strong').length, 1);
  assert.strictEqual(div.querySelector('strong').textContent, '強調');
  assert.ok(div.textContent.includes('$a_{**}$'), 'inline math kept verbatim');
});

/* ==== D1: paragraph split + soft-newline join ==== */
check('(D1) blank line splits paragraphs; single newline joins without a break', () => {
  assert.strictEqual(splitParagraphs('段落一\n\n段落二').length, 2);
  assert.strictEqual(joinSoftLines('あ\nい'), 'あい');          // CJK↔CJK: no space
  assert.strictEqual(joinSoftLines('ab\ncd'), 'ab cd');         // ASCII↔ASCII: one space
  assert.strictEqual(joinSoftLines('あ\nb'), 'あb');            // mixed: no space
  const div = document.createElement('div');
  renderProse(div, '一行目\n二行目\n\n次段落');
  assert.strictEqual(div.querySelectorAll('p.prose-p').length, 2);
  assert.ok(div.querySelector('p.prose-p').textContent.includes('一行目二行目'));
});

check('(D1) hovercard preview cuts at a sentence boundary, never mid-sentence', () => {
  const s = '短い最初の文。' + 'あ'.repeat(200) + '。';
  const preview = sentencePreview(s, 90);
  assert.ok(preview.endsWith('。'), 'preview ends at a 。 boundary');
  assert.ok(preview.length <= 200, 'preview respects the budget by cutting at 。');
});

/* ==== 受け入れ基準 5: gap Note sits below the proof band ==== */
check('(d) gap Note renders after the proof band and before uses', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.trail = [];
  state.chapterMeta.set('capstone-r3', { id: 'capstone-r3', label_ja: 'ℝ³ 主定理' });
  state.data = { nodes: [], chapters: [] };
  const decl = {
    slug: 'cap', id: 'cap', name: 'LerayHopf.cap', shortName: 'cap', kind: 'theorem',
    private: false, signature: 'theorem cap : True', doc: '', file: 'X.lean',
    startLine: 1, endLine: 2, chapter: 'capstone-r3', uses: [], usedBy: [],
    collision: false, capstone: true, has_source: false,
    corpus: {
      tier: 'full', statement_ja: '主張の本文。', proof_ja: '証明の本文。',
      gap: { level: 'large', note: '形式化ギャップの説明。' }, tags: [], sample: false,
    },
  };
  state.bySlug.set('cap', decl);
  renderDecl(appEl, 'cap');

  const kids = Array.from(appEl.children);
  const isSection = (h) => (c) => c.classList && c.classList.contains('section')
    && c.querySelector('h3') && h(c.querySelector('h3').textContent);
  const proofIdx = kids.findIndex(isSection((t) => t === '証明'));
  const gapIdx = kids.findIndex((c) => c.id === 'gap-note');
  const usesIdx = kids.findIndex(isSection((t) => t.startsWith('直接依存宣言')));
  assert.ok(proofIdx >= 0, 'proof section present');
  assert.ok(gapIdx >= 0, 'gap-note panel present');
  assert.ok(usesIdx >= 0, 'uses section present');
  assert.ok(gapIdx > proofIdx, 'gap Note must come AFTER the proof band');
  assert.ok(gapIdx < usesIdx, 'gap Note must come BEFORE the uses section');
});

check('source payload is lazy-loaded from data/sources.json by slug', async () => {
  state.sources = null;
  state.sourcesPromise = null;
  state.data = { source_payload: 'sources.json' };
  const oldFetch = global.fetch;
  let calls = 0;
  global.fetch = async (url) => {
    calls += 1;
    assert.strictEqual(url, 'data/sources.json');
    return {
      ok: true,
      json: async () => ({ sources: { cap: 'theorem cap : True := by trivial' } }),
    };
  };
  try {
    const src = await loadSourceFor({ slug: 'cap', has_source: true });
    assert.strictEqual(src, 'theorem cap : True := by trivial');
    assert.strictEqual(calls, 1);
  } finally {
    global.fetch = oldFetch;
    state.sources = null;
    state.sourcesPromise = null;
  }
});

/* ==== notes#65: proof_status badge / banner — must not look like a proved theorem ==== */
check('(e) proofStatusBadge renders nothing for the default verified status (absent/verified)', () => {
  assert.strictEqual(proofStatusBadge(undefined), null, 'no badge when proof_status is absent');
  assert.strictEqual(proofStatusBadge('verified'), null, 'no badge for explicit verified');
  assert.strictEqual(proofStatusBanner(undefined), null, 'no banner when proof_status is absent');
});

check('(e) proofStatusBadge renders a distinct badge for every non-verified status', () => {
  for (const status of ['contains-sorry', 'scaffold', 'retired', 'invalid-statement']) {
    const b = proofStatusBadge(status);
    assert.ok(b, `badge must exist for ${status}`);
    assert.ok(b.className.includes('proof-status'), `badge must carry the proof-status class for ${status}`);
    assert.ok(b.textContent.trim().length > 0, `badge must have visible label text for ${status}`);
  }
});

check('(f) renderDecl shows a prominent proof-status banner for contains-sorry, positioned right after the header (before 主張)', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.trail = [];
  state.chapterMeta.set('bochner', { id: 'bochner', label_ja: 'Bochner 時間層' });
  state.data = { nodes: [], chapters: [] };
  const decl = {
    slug: 'sorryDecl', id: 'sorryDecl', name: 'LerayHopf.Bochner.sorryDecl', shortName: 'sorryDecl',
    kind: 'theorem', private: false, signature: 'theorem sorryDecl : True', doc: '', file: 'X.lean',
    startLine: 1, endLine: 2, chapter: 'bochner', uses: [], usedBy: [],
    collision: false, capstone: false, has_source: false,
    corpus: {
      tier: 'full', statement_ja: '主張の本文。', proof_ja: '証明の本文。',
      gap: { level: 'large', note: '形式化コストの説明。' }, tags: [], sample: false,
      proof_status: 'contains-sorry',
    },
  };
  state.bySlug.set('sorryDecl', decl);
  renderDecl(appEl, 'sorryDecl');

  const banner = appEl.querySelector('.proof-status-banner');
  assert.ok(banner, 'a .proof-status-banner must be rendered for contains-sorry');
  assert.ok(banner.classList.contains('proof-sorry'), 'banner must carry the sorry-specific style class');
  assert.ok(banner.textContent.includes('sorry'), 'banner text must name the sorry status');

  const metaBadge = appEl.querySelector('.meta-row .badge.proof-status');
  assert.ok(metaBadge, 'the header meta-row must also carry a proof-status badge');

  const kids = Array.from(appEl.children);
  const bannerIdx = kids.indexOf(banner);
  const isSection = (h) => (c) => c.classList && c.classList.contains('section')
    && c.querySelector('h3') && h(c.querySelector('h3').textContent);
  const stmtIdx = kids.findIndex(isSection((t) => t === '主張'));
  assert.ok(bannerIdx >= 0 && stmtIdx >= 0 && bannerIdx < stmtIdx,
    'the banner must appear before the 主張 section, not buried below the fold');
});

check('(f-regression) renderDecl shows no proof-status banner for an ordinary verified declaration', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.trail = [];
  state.data = { nodes: [], chapters: [] };
  const decl = {
    slug: 'plainDecl', id: 'plainDecl', name: 'LerayHopf.plainDecl', shortName: 'plainDecl',
    kind: 'theorem', private: false, signature: 'theorem plainDecl : True', doc: '', file: 'X.lean',
    startLine: 1, endLine: 2, chapter: 'bochner', uses: [], usedBy: [],
    collision: false, capstone: false, has_source: false,
    corpus: {
      tier: 'full', statement_ja: '主張の本文。', proof_ja: '証明の本文。',
      gap: { level: 'none' }, tags: [], sample: false, proof_status: 'verified',
    },
  };
  state.bySlug.set('plainDecl', decl);
  renderDecl(appEl, 'plainDecl');
  assert.strictEqual(appEl.querySelector('.proof-status-banner'), null,
    'a verified declaration must not show any proof-status banner');
  assert.strictEqual(appEl.querySelector('.meta-row .badge.proof-status'), null,
    'a verified declaration must not show a proof-status badge');
});

check('(g) renderDecl shows a 参考文献 panel with resolved citation text when corpus.references is set', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.trail = [];
  state.data = {
    nodes: [], chapters: [],
    bibliography: { temam2001: 'Temam, R. (2001). Navier-Stokes Equations...' },
  };
  const decl = {
    slug: 'refDecl', id: 'refDecl', name: 'LerayHopf.refDecl', shortName: 'refDecl',
    kind: 'theorem', private: false, signature: 'theorem refDecl : True', doc: '', file: 'X.lean',
    startLine: 1, endLine: 2, chapter: 'bochner', uses: [], usedBy: [],
    collision: false, capstone: false, has_source: false,
    corpus: {
      tier: 'full', statement_ja: '主張の本文。', proof_ja: '証明の本文。',
      gap: { level: 'none' }, tags: [], sample: false, proof_status: 'verified',
      references: [{ id: 'temam2001', locator: 'III.3' }],
    },
  };
  state.bySlug.set('refDecl', decl);
  renderDecl(appEl, 'refDecl');
  const panel = appEl.querySelector('.refs-panel');
  assert.ok(panel, 'a declaration with corpus.references must render a 参考文献 panel');
  assert.ok(panel.textContent.includes('III.3'), 'the locator must be shown');
  assert.ok(panel.textContent.includes('Temam, R. (2001)'),
    'the resolved bibliography citation text must be shown, not just the bare id');
  const link = panel.querySelector('a');
  assert.ok(link && link.getAttribute('href') === '#/about/temam2001',
    'the citation id must link to its /about entry');
});

check('(g-regression) renderDecl shows no 参考文献 panel when corpus.references is absent', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.trail = [];
  state.data = { nodes: [], chapters: [], bibliography: {} };
  const decl = {
    slug: 'noRefDecl', id: 'noRefDecl', name: 'LerayHopf.noRefDecl', shortName: 'noRefDecl',
    kind: 'theorem', private: false, signature: 'theorem noRefDecl : True', doc: '', file: 'X.lean',
    startLine: 1, endLine: 2, chapter: 'bochner', uses: [], usedBy: [],
    collision: false, capstone: false, has_source: false,
    corpus: {
      tier: 'full', statement_ja: '主張の本文。', proof_ja: '証明の本文。',
      gap: { level: 'none' }, tags: [], sample: false, proof_status: 'verified',
    },
  };
  state.bySlug.set('noRefDecl', decl);
  renderDecl(appEl, 'noRefDecl');
  assert.strictEqual(appEl.querySelector('.refs-panel'), null,
    'a declaration without corpus.references must not render a 参考文献 panel');
});

check('(i) renderDecl shows a collapsed 開発履歴 panel, closed by default, when corpus.provenance is set', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.trail = [];
  state.data = { nodes: [], chapters: [], bibliography: {} };
  const decl = {
    slug: 'provDecl', id: 'provDecl', name: 'LerayHopf.provDecl', shortName: 'provDecl',
    kind: 'theorem', private: false, signature: 'theorem provDecl : True', doc: '', file: 'X.lean',
    startLine: 1, endLine: 2, chapter: 'bochner', uses: [], usedBy: [],
    collision: false, capstone: false, has_source: false,
    corpus: {
      tier: 'full', statement_ja: '主張の本文。', proof_ja: '証明の本文。',
      gap: { level: 'none' }, tags: [], sample: false, proof_status: 'verified',
      provenance: 'lean-pde issue #999 で公開移動。',
    },
  };
  state.bySlug.set('provDecl', decl);
  renderDecl(appEl, 'provDecl');
  const panel = appEl.querySelector('.provenance-panel');
  assert.ok(panel, 'a declaration with corpus.provenance must render a provenance panel');
  const det = panel.querySelector('details');
  assert.ok(det, 'the provenance panel must use a <details> toggle');
  assert.strictEqual(det.hasAttribute('open'), false,
    'the provenance <details> must be closed by default (notes#69: history is demoted, not deleted)');
  assert.ok(panel.textContent.includes('issue #999'),
    'the provenance text itself must still be present in the DOM (not lost) even though collapsed');
  assert.ok(det.querySelector('summary').textContent.includes('開発履歴'),
    'the toggle summary must be labeled as development history');
});

check('(i-regression) renderDecl shows no provenance panel when corpus.provenance is absent', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.trail = [];
  state.data = { nodes: [], chapters: [], bibliography: {} };
  const decl = {
    slug: 'noProvDecl', id: 'noProvDecl', name: 'LerayHopf.noProvDecl', shortName: 'noProvDecl',
    kind: 'theorem', private: false, signature: 'theorem noProvDecl : True', doc: '', file: 'X.lean',
    startLine: 1, endLine: 2, chapter: 'bochner', uses: [], usedBy: [],
    collision: false, capstone: false, has_source: false,
    corpus: {
      tier: 'full', statement_ja: '主張の本文。', proof_ja: '証明の本文。',
      gap: { level: 'none' }, tags: [], sample: false, proof_status: 'verified',
    },
  };
  state.bySlug.set('noProvDecl', decl);
  renderDecl(appEl, 'noProvDecl');
  assert.strictEqual(appEl.querySelector('.provenance-panel'), null,
    'a declaration without corpus.provenance must not render a provenance panel');
});

check('(h) renderAbout lists bibliography entries, shows citation/license metadata, and highlights the requested id', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.data = {
    nodes: [], chapters: [],
    pin: 'abc123deadbeef',
    built_at: '2026-07-17T00:00:00Z',
    citation: {
      authors: ['Tomoki Uda'],
      repository_code: 'https://github.com/uda-lab/leray-hopf-notes',
      source_repository: 'https://github.com/uda-lab/leray-hopf',
      source_commit: 'abc123deadbeef',
      license: ['Apache-2.0', 'CC-BY-4.0'],
      license_url: 'https://github.com/uda-lab/leray-hopf-notes/blob/main/LICENSE.md',
    },
    bibliography: {
      temam2001: 'Temam, R. (2001). Navier-Stokes Equations...',
      rrs2016: 'Robinson, J.C., Rodrigo, J.L., Sadowski, W. (2016). The Three-Dimensional...',
    },
  };
  renderAbout(appEl, 'rrs2016');
  assert.ok(appEl.textContent.includes('semantic proof certification')
    || appEl.textContent.includes('数学的に正しいことを証明・認証するものではない'),
    'the /about page must state the non-certification disclaimer');
  assert.ok(appEl.textContent.includes('Tomoki Uda'), 'author must be shown');
  assert.ok(appEl.textContent.includes('Apache-2.0') && appEl.textContent.includes('CC-BY-4.0'),
    'the split license must be shown');
  assert.ok(appEl.textContent.includes('abc123deadbeef'), 'the exact source pin must be shown');
  const pinLink = Array.from(appEl.querySelectorAll('a')).find(a => a.textContent === 'abc123deadbeef');
  assert.ok(pinLink && pinLink.getAttribute('href').includes('abc123deadbeef'),
    'the pin must be a clickable link to the exact-commit source tree');
  assert.ok(appEl.querySelector('#ref-temam2001') && appEl.querySelector('#ref-rrs2016'),
    'every bibliography entry must be listed');
  const highlighted = appEl.querySelector('.ref-highlight');
  assert.ok(highlighted && highlighted.id === 'ref-rrs2016',
    'the id passed to renderAbout must be highlighted');
});

/* ==== notes#72: accessibility — DAG toggle is a real, keyboard-operable control ==== */
check('(i) dagItem renders the expand toggle as a real <button> with aria-expanded, toggling on click', () => {
  addNode({
    slug: 'X.dagChild', id: 'X.dagChild', name: 'X.dagChild', shortName: 'dagChild', kind: 'def',
    signature: 'def dagChild', file: 'X.lean', startLine: 1, endLine: 1,
    chapter: 'spaces', uses: [], usedBy: [], private: false, corpus: null,
  });
  const parent = {
    slug: 'X.dagParent', name: 'X.dagParent', shortName: 'dagParent', kind: 'theorem',
    uses: ['X.dagChild'], usedBy: [], private: false, corpus: null,
  };
  const li = dagItem(parent, new Set(['X.dagParent']));
  const twist = li.querySelector('.twist');
  assert.strictEqual(twist.tagName, 'BUTTON', 'the expand toggle must be a real <button>, not a clickable <span>');
  assert.strictEqual(twist.getAttribute('aria-expanded'), 'false', 'starts collapsed');
  twist.dispatchEvent(new window.Event('click', { bubbles: true }));
  assert.strictEqual(twist.getAttribute('aria-expanded'), 'true', 'aria-expanded must flip to true on expand');
  assert.ok(li.querySelector('ul'), 'expanding must render the children <ul>');
});

check('(i-regression) a leaf dagItem (no uses) renders a decorative, non-interactive <span>', () => {
  const leaf = {
    slug: 'X.dagLeaf', name: 'X.dagLeaf', shortName: 'dagLeaf', kind: 'def',
    uses: [], usedBy: [], private: false, corpus: null,
  };
  const li = dagItem(leaf, new Set(['X.dagLeaf']));
  const twist = li.querySelector('.twist');
  assert.strictEqual(twist.tagName, 'SPAN', 'a leaf has no expand action — it must stay a non-interactive <span>');
  assert.strictEqual(twist.getAttribute('aria-hidden'), 'true');
});

/* ==== notes#72: [[…]] refs are real <a> links, reachable by Tab ==== */
check('(j) makeRef renders a resolved reference as a real <a href>, not a plain <span>', () => {
  const ref = makeRef('lerayProjection|LerayHopf.lerayProjection', []);
  assert.strictEqual(ref.tagName, 'A', 'a resolved ref must be a real <a> so keyboard Tab reaches it');
  assert.ok(ref.getAttribute('href'), 'the <a> must carry an href');
  assert.strictEqual(ref.className, 'ref');
});

check('(j-regression) an unresolved reference stays a non-interactive <span>', () => {
  const ref = makeRef('nonexistent thing', []);
  assert.strictEqual(ref.tagName, 'SPAN', 'an unresolved ref has no navigation target');
  assert.ok(ref.className.includes('ref-missing'));
});

/* ==== notes#72: progress bar carries ARIA progressbar semantics ==== */
check('(k) progressBar renders role=progressbar with aria-value* and sets fill width as a JS style property', () => {
  const bar = progressBar(42, 'テストラベル 42%');
  assert.strictEqual(bar.getAttribute('role'), 'progressbar');
  assert.strictEqual(bar.getAttribute('aria-valuenow'), '42');
  assert.strictEqual(bar.getAttribute('aria-valuemin'), '0');
  assert.strictEqual(bar.getAttribute('aria-valuemax'), '100');
  assert.strictEqual(bar.getAttribute('aria-label'), 'テストラベル 42%');
  const fill = bar.querySelector('span');
  // Width is set via the .style CSSOM property (not el()'s style: attrs path, which
  // uses setAttribute('style', …)) so a CSP `style-src 'self'` with no 'unsafe-inline'
  // does not block it — see the comment on progressBar() for the CSP distinction.
  assert.strictEqual(fill.style.width, '42%');
});

check('(k-regression) progressBar clamps out-of-range percentages into [0, 100]', () => {
  assert.strictEqual(progressBar(150).getAttribute('aria-valuenow'), '100');
  assert.strictEqual(progressBar(-5).getAttribute('aria-valuenow'), '0');
});

/* ==== notes#72: coverage table has caption/thead/tbody/scope ==== */
check('(l) renderCoverage emits a table with caption, thead, tbody, and scoped headers', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.coverage = {
    pct_annotated: 80, annotated: 8, total_decls: 10, full: 5, gloss: 3,
    chapters: { spaces: { annotated: 8, full: 5, gloss: 3 } },
  };
  state.data = { chapters: [{ id: 'spaces', label_ja: '空間' }] };
  state.chapterTotals.set('spaces', 10);
  renderCoverage(appEl);
  const table = appEl.querySelector('table.coverage');
  assert.ok(table, 'a table.coverage must be rendered');
  assert.ok(table.querySelector('caption'), 'the table must have a <caption>');
  assert.ok(table.querySelector('thead'), 'the header row must be inside <thead>');
  assert.ok(table.querySelector('tbody'), 'the data rows must be inside <tbody>');
  const colHeaders = table.querySelectorAll('thead th');
  assert.ok(colHeaders.length > 0 && Array.from(colHeaders).every(th => th.getAttribute('scope') === 'col'),
    'every column header must carry scope="col"');
  const rowHeader = table.querySelector('tbody th');
  assert.ok(rowHeader && rowHeader.getAttribute('scope') === 'row',
    'the chapter-name cell must be a <th scope="row">, not a <td>');
});

/* ==== notes#72: esc() also escapes quotes (attribute-interpolation safety) ==== */
check('(m) esc() escapes quotes as well as &<>, since highlightLean() interpolates it into a quoted attribute', () => {
  assert.strictEqual(esc('a"b\'c&d<e>f'), 'a&quot;b&#39;c&amp;d&lt;e&gt;f');
});

/* ==== notes#72: route() moves focus to the new page's own <h1> instead of a blanket
 * aria-live region, so screen readers announce just the new page heading. ==== */
check('(n) route() moves focus to the rendered page\'s <h1> with tabindex="-1"', () => {
  state.data = { chapters: [], capstones: [] };
  window.location.hash = '#/dag';
  route();
  const h1 = document.getElementById('app').querySelector('h1');
  assert.ok(h1, 'the DAG page must render an <h1>');
  assert.strictEqual(h1.getAttribute('tabindex'), '-1', 'the heading must be a valid focus() target');
  assert.strictEqual(document.activeElement, h1, 'focus must move to the new page heading after routing');
});

/* ==== notes#72 (codex review): the skip link must not be swallowed by the hash router.
 * route() treats every hash as a route (see test (n)'s fixture); href="#app" matches no
 * route, so without interception it renders "ページが見つかりません" instead of just
 * moving focus past the header. ==== */
check('(o) setupSkipLink prevents the skip link\'s href="#app" from being treated as a route change', () => {
  // The real site/index.html gives #app tabindex="-1" so it's a valid focus() target;
  // replicate that here since the minimal jsdom fixture doesn't otherwise carry it.
  document.getElementById('app').setAttribute('tabindex', '-1');
  const skipLink = document.createElement('a');
  skipLink.className = 'skip-link';
  skipLink.href = '#app';
  document.body.insertBefore(skipLink, document.body.firstChild);
  setupSkipLink();
  const ev = new window.MouseEvent('click', { bubbles: true, cancelable: true });
  const notCancelled = skipLink.dispatchEvent(ev);
  assert.strictEqual(notCancelled, false,
    'the click must be preventDefault()ed so location.hash never actually becomes "#app"');
  assert.strictEqual(document.activeElement, document.getElementById('app'),
    'focus must move directly to #app, bypassing hash navigation entirely');
  skipLink.remove();
});

/* ==== notes#72 (codex review): keyboard activation of a resolved ref must navigate,
 * not just show the pinned preview card — the card's own "open" link isn't reliably
 * reachable by a further Tab press (it lives at the end of <body>, not next to the ref
 * in DOM/tab order), so intercepting keyboard Enter the same as a mouse click left
 * keyboard users with no way to actually follow the reference. ==== */
check('(p) a keyboard-triggered activation (MouseEvent.detail === 0) on a resolved ref navigates instead of pinning the preview', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  const ref = makeRef('lerayProjection|LerayHopf.lerayProjection', []);
  appEl.appendChild(ref);
  bindHoverCards();
  const ev = new window.MouseEvent('click', { bubbles: true, cancelable: true, detail: 0 });
  const notCancelled = ref.dispatchEvent(ev);
  assert.strictEqual(notCancelled, true,
    'a keyboard-triggered activation (Enter on a focused link fires a click with detail 0) must not be prevented');
});

check('(p-regression) a real mouse click (MouseEvent.detail >= 1) on a resolved ref still pins the preview card', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  const ref = makeRef('lerayProjection|LerayHopf.lerayProjection', []);
  appEl.appendChild(ref);
  bindHoverCards();
  const ev = new window.MouseEvent('click', { bubbles: true, cancelable: true, detail: 1 });
  const notCancelled = ref.dispatchEvent(ev);
  assert.strictEqual(notCancelled, false, 'a real mouse click must still be intercepted to show the pinned preview');
  assert.strictEqual(document.getElementById('hovercard').hidden, false, 'the preview card must be shown');
});

/* ==== notes#71: graph terminology + no hard-coded declaration counts in UI prose ==== */
check('(q) DAG page uses accurate graph terminology (宣言依存グラフ, not 証明ツリー) and a dynamic node count', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  state.data = { capstones: [], decl_count: 1339, chapters: [] };
  renderDag(appEl);
  const text = appEl.textContent;
  assert.ok(text.includes('宣言依存グラフ'), 'DAG page must use the accurate graph label');
  assert.ok(!text.includes('証明ツリー'), 'DAG page must not call this a proof tree');
  assert.ok(text.includes('1,339'), 'the "does not render everything" note must reflect the live decl_count, not a hard-coded literal');
});

check('(q) empty usedBy state does not conflate "no incoming edges" with "leaf" (no outgoing edges)', () => {
  const appEl = document.getElementById('app');
  appEl.innerHTML = '';
  const node = { usedBy: [], uses: ['something'] }; // has outgoing edges -> not a leaf, but still no usedBy
  renderUsedBy(appEl, node);
  const text = appEl.textContent;
  assert.ok(!text.includes('葉'), 'a node with outgoing edges must not be described as a leaf just because it has no usedBy');
});

/* ==== notes#73: route-aware document.title / meta description / canonical ==== */
check('(r) stripMarkupForMeta removes $…$ math, **bold**, `code`, and [[display|target]] ref markers', () => {
  const out = stripMarkupForMeta('a $x^2$ b **強調** c `code` d [[表示|LerayHopf.foo]] e');
  assert.ok(!out.includes('$'), 'math delimiters must be stripped');
  assert.ok(!out.includes('**'), 'bold markers must be stripped');
  assert.ok(!out.includes('`'), 'code markers must be stripped');
  assert.ok(out.includes('表示') && !out.includes('[['), 'ref display text is kept, brackets/target dropped');
});

check('(r) renderHome sets the default site title/description (no route-specific override)', () => {
  state.data = { chapters: [], capstones: [] };
  window.location.hash = '#/';
  route();
  assert.strictEqual(document.title, DEFAULT_TITLE);
  assert.strictEqual(document.querySelector('meta[name="description"]').getAttribute('content'), DEFAULT_DESCRIPTION);
});

check('(r) route() to a decl page sets document.title to the fully-qualified name and a markup-free description', () => {
  state.data = { chapters: [], capstones: [] };
  window.location.hash = '#/decl/' + encodeURIComponent('LerayHopf.weakSolutionExists');
  route();
  assert.strictEqual(document.title, 'LerayHopf.weakSolutionExists — leray-hopf-notes');
  const desc = document.querySelector('meta[name="description"]').getAttribute('content');
  assert.ok(desc.includes('弱解') && !desc.includes('$') && !desc.includes('**'),
    'decl description must be derived from statement_ja with math/markdown stripped');
  const canonical = document.querySelector('link[rel="canonical"]');
  assert.ok(canonical, 'a <link rel="canonical"> must exist');
  assert.strictEqual(canonical.getAttribute('href'), location.href, 'canonical href must track the current route');
  assert.strictEqual(document.querySelector('meta[property="og:title"]').getAttribute('content'), 'LerayHopf.weakSolutionExists');
});

check('(r) route() to an unknown hash sets a "not found" title instead of leaking the previous page\'s metadata', () => {
  window.location.hash = '#/decl/' + encodeURIComponent('LerayHopf.weakSolutionExists');
  route();
  window.location.hash = '#/does-not-exist';
  route();
  assert.strictEqual(document.title, 'ページが見つかりません — leray-hopf-notes');
});

check('(r) search matches tags/proof_ja/doc in addition to name/statement_ja, and title/description reflect the query', () => {
  state.data = { chapters: [], capstones: [], nodes: [state.bySlug.get('LerayHopf.weakSolutionExists')] };
  window.location.hash = '#/search/' + encodeURIComponent('existence-uniqueness');
  route();
  assert.strictEqual(document.title, '検索: existence-uniqueness — leray-hopf-notes');
  const appEl = document.getElementById('app');
  assert.ok(appEl.textContent.includes('1 件'), 'a tag-only match must still be counted as a hit');
  const desc = document.querySelector('meta[name="description"]').getAttribute('content');
  assert.ok(desc.includes('1 件'), 'search meta description must report the hit count');
  // notes#73 (codex pre-review): setPageMeta() runs before hits are counted and left
  // og:description at the site default for any non-empty query — renderSearch must
  // update it again once the hit count is known, not just the plain meta description.
  const ogDesc = document.querySelector('meta[property="og:description"]').getAttribute('content');
  assert.ok(ogDesc.includes('1 件'), 'og:description must also report the hit count, not the stale site default');
});

Promise.all(pending).then(() => {
  console.log(`\nAll ${passed} render checks passed.`);
}).catch((err) => {
  console.error(err);
  process.exit(1);
});
