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

const app = require('../site/app.js');
const {
  state, splitParagraphs, joinSoftLines, firstParagraph, sentencePreview,
  renderProse, renderProseInline, renderDecl, loadSourceFor,
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
  const usesIdx = kids.findIndex(isSection((t) => t.startsWith('依存補題')));
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

Promise.all(pending).then(() => {
  console.log(`\nAll ${passed} render checks passed.`);
}).catch((err) => {
  console.error(err);
  process.exit(1);
});
