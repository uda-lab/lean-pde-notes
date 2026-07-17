#!/usr/bin/env python3
"""
prose_lint.py — prose typography / register linter for leray-hopf-notes (notes#12).

Complements glossary_lint.py (vocabulary) with the D1–D5 typography rules:

  D1  intra-paragraph newlines — prose fields are authored one physical line per
      paragraph, blank line = paragraph boundary. A single \n inside a paragraph is a
      hard error (the renderer collapses it, so it is silent breakage waiting to happen).
  D2  Lean identifiers in math — a Lean declaration name (camelCase, or an escaped/raw
      underscore) inside $…$ / $$…$$ is a hard error. Natural mathematical notation and
      意訳語 only. Overlong / structurally-heavy inline math (fractions, big operators)
      is a soft warning: prefer display math $$…$$.
  D5  unsupported markdown — headings, lists, blockquotes, links/images, and unbalanced
      ** / backtick / [[ … ]] are hard errors (only `code`, **strong**, [[ref]] and KaTeX
      are supported inline; everything else renders literally).

Exit code:
  * hard errors present            -> exit 1 (default; the gate)
  * only soft warnings             -> exit 0 (report only), or exit 1 with --strict

Usage:
    python3 scripts/prose_lint.py
    python3 scripts/prose_lint.py --strict
    python3 scripts/prose_lint.py --corpus corpus/LerayHopf/
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit('ERROR: PyYAML required. pip install pyyaml')

REPO_ROOT = Path(__file__).parent.parent
CORPUS_DIR = REPO_ROOT / 'corpus'

PROSE_FIELDS = ('statement_ja', 'proof_ja')   # gap.note handled separately (nested)

# Math span: $$…$$ (display) or $…$ (inline). Display first so it wins.
MATH_RE = re.compile(r'\$\$.+?\$\$|\$[^$]+?\$', re.DOTALL)
DISPLAY_MATH_RE = re.compile(r'^\$\$.+\$\$$', re.DOTALL)

# \mathrm{…}/\text{…}/\operatorname{…} whose braces carry a Lean-name shape.
MATHRM_RE = re.compile(r'\\(?:mathrm|text|operatorname|mathsf|mathtt|mathbf)\s*\{([^{}]*)\}')
# camelCase transition (lower/digit -> upper) — the divTestFunctional / h1EnergySq signal.
CAMEL_RE = re.compile(r'[a-z0-9][A-Z]')
# bare Lean-ish token in math: starts lowercase, not preceded by backslash/alnum, has an
# internal uppercase (mFourierCoeff3, galSeq, starProjection, fourierProjection …).
BARE_CAMEL_RE = re.compile(r'(?<![\\A-Za-z0-9])[a-z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*')

# D5 unsupported-markdown line signals.
HEADING_RE = re.compile(r'^\s{0,3}#{1,6}\s')
ULIST_RE = re.compile(r'^\s{0,3}[-+]\s')
OLIST_RE = re.compile(r'^\s{0,3}\d+\.\s')
BLOCKQUOTE_RE = re.compile(r'^\s{0,3}>\s')
LINK_RE = re.compile(r'!?\[[^\]]*\]\([^)]*\)')


def zen_len(s: str) -> int:
    """Full-width-equivalent length: wide/ambiguous CJK = 1, ASCII = 0.5 (rounded up)."""
    total = 0.0
    for ch in s:
        total += 1.0 if unicodedata.east_asian_width(ch) in ('W', 'F', 'A') else 0.5
    return int(total + 0.5)


def strip_supported_inline(text: str) -> str:
    """Remove supported inline constructs (code / strong / ref) so the residue can be
    scanned for unsupported markdown. Math is already excised by the caller."""
    text = re.sub(r'`[^`]*`', '', text)          # `code`
    text = re.sub(r'\*\*.+?\*\*', '', text, flags=re.DOTALL)  # **strong**
    text = re.sub(r'\[\[[^\]]*\]\]', '', text)   # [[ref]] / [[disp|target]]
    return text


def check_math(math: str, display: bool) -> list[str]:
    findings = []  # (severity, message)
    inner = math.strip('$')
    # D2 hard: Lean name inside \mathrm{…}/\text{…}
    for m in MATHRM_RE.finditer(math):
        g = m.group(1)
        if CAMEL_RE.search(g) or '_' in g or '\\_' in g:
            findings.append(('error', f'Lean 識別子とみられる名前が数式内: \\mathrm{{{g}}}'))
    # D2 hard: escaped underscore (Lean snake/camel name written in TeX)
    if '\\_' in math:
        findings.append(('error', f'数式内にエスケープ下線 \\_ （Lean 宣言名の疑い）: {math[:48]}'))
    # D2 hard: bare camelCase token
    commandless = re.sub(r'\\[A-Za-z]+', ' ', math)
    for m in BARE_CAMEL_RE.finditer(commandless):
        findings.append(('error', f'数式内に camelCase 生トークン（Lean 名の疑い）: {m.group(0)}'))
    # D2 soft: overlong / heavy inline math -> prefer display
    if not display:
        heavy = re.search(r'\\frac|\\d?frac|\\sum_|\\int_|\\prod_|\\begin\{', inner)
        if zen_len(inner) > 20 or (heavy and zen_len(inner) > 14):
            findings.append(('warn', f'インライン数式が長い/重い — ディスプレイ $$…$$ を検討: ${inner[:40]}…$'))
    return findings


def check_field(field_name: str, raw: str) -> list[str]:
    findings = []
    text = raw.strip('\n')
    if not text.strip():
        return findings

    # D1: intra-paragraph newlines (paragraphs are blank-line separated; no \n inside one).
    paragraphs = re.split(r'\n[ \t]*\n', text)
    for para in paragraphs:
        if '\n' in para.strip('\n'):
            snippet = para.strip().split('\n')[0][:40]
            findings.append(('error',
                f'{field_name}: 段落内に改行（1 段落 = 1 物理行, D1）: 「{snippet}…」'))

    # Scan math spans (D2), then strip them for the markdown residue scan (D5).
    for m in MATH_RE.finditer(text):
        span = m.group(0)
        display = bool(DISPLAY_MATH_RE.match(span))
        for sev, msg in check_math(span, display):
            findings.append((sev, f'{field_name}: {msg}'))
    no_math = MATH_RE.sub(' ', text)

    # D5: unsupported markdown on the math-free, supported-inline-free residue.
    residue = strip_supported_inline(no_math)
    for line in residue.split('\n'):
        if HEADING_RE.match(line):
            findings.append(('error', f'{field_name}: 見出し記法は非対応 (D5): 「{line.strip()[:40]}」'))
        if ULIST_RE.match(line) or OLIST_RE.match(line):
            findings.append(('error', f'{field_name}: リスト記法は非対応 (D5): 「{line.strip()[:40]}」'))
        if BLOCKQUOTE_RE.match(line):
            findings.append(('error', f'{field_name}: 引用記法は非対応 (D5): 「{line.strip()[:40]}」'))
    if LINK_RE.search(residue):
        findings.append(('error', f'{field_name}: リンク/画像記法は非対応 (D5)'))
    # Unbalanced supported markers left after stripping balanced pairs.
    if '`' in residue:
        findings.append(('error', f'{field_name}: 対応の取れないバックティックが残存 (D5)'))
    if '**' in residue:
        findings.append(('error', f'{field_name}: 対応の取れない ** が残存 (D5)'))
    if '[[' in residue or ']]' in residue:
        findings.append(('error', f'{field_name}: 対応の取れない [[ / ]] が残存 (D5)'))
    return findings


def lint_doc(fpath: Path, doc: dict) -> list[str]:
    out = []
    for field in PROSE_FIELDS:
        val = doc.get(field)
        if isinstance(val, str):
            out.extend(check_field(field, val))
    gap = doc.get('gap')
    if isinstance(gap, dict) and isinstance(gap.get('note'), str):
        out.extend(check_field('gap.note', gap['note']))
    return [(sev, f'{fpath.relative_to(REPO_ROOT)}: {msg}') for sev, msg in out]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--strict', action='store_true',
                        help='Exit 1 on soft warnings too (default: only hard errors gate)')
    parser.add_argument('--corpus', default=None, help='Lint only this subtree')
    args = parser.parse_args()

    root = Path(args.corpus) if args.corpus else CORPUS_DIR
    if not root.is_dir():
        sys.exit(f'ERROR: corpus directory not found: {root}')

    files = sorted(root.rglob('*.yaml'))
    errors, warns = [], []
    for fpath in files:
        try:
            with open(fpath, encoding='utf-8') as f:
                doc = yaml.safe_load(f)
        except (yaml.YAMLError, OSError) as exc:
            errors.append(f'{fpath.relative_to(REPO_ROOT)}: parse error: {exc}')
            continue
        if not isinstance(doc, dict):
            continue
        for sev, msg in lint_doc(fpath, doc):
            (errors if sev == 'error' else warns).append(msg)

    if errors:
        print(f'{len(errors)} error(s):')
        for e in errors:
            print(f'  ERROR {e}')
    if warns:
        print(f'{len(warns)} warning(s):')
        for w in warns:
            print(f'  WARN  {w}')
    if not errors and not warns:
        print(f'OK — {len(files)} corpus file(s) checked, no prose findings.')
    elif not errors:
        print(f'\nOK (no hard errors) — {len(files)} corpus file(s) checked.')

    if errors or (args.strict and warns):
        sys.exit(1)


if __name__ == '__main__':
    main()
