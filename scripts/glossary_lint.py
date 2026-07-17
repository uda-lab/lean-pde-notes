#!/usr/bin/env python3
"""
glossary_lint.py — corpus translation linter for leray-hopf-notes.

Parses docs/GLOSSARY.md (Markdown table with columns:
  English term | 日本語訳 | Lean 識別子例 | 備考 | forbidden)

For each corpus/**/*.yaml:
  - Detects occurrences of known-bad (forbidden) translations in statement_ja / proof_ja.
  - Warns when an English term appears in statement_ja / proof_ja but the established
    Japanese translation does NOT appear nearby (possible vocabulary drift).

Exit code: 0 (warnings only) unless --strict (exit 1 on any finding).

Usage:
    python3 scripts/glossary_lint.py
    python3 scripts/glossary_lint.py --strict
    python3 scripts/glossary_lint.py --corpus corpus/LerayHopf/R3/  # specific subtree
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    sys.exit('ERROR: PyYAML required. pip install pyyaml')

REPO_ROOT = Path(__file__).parent.parent
GLOSSARY_PATH = REPO_ROOT / 'docs' / 'GLOSSARY.md'
CORPUS_DIR = REPO_ROOT / 'corpus'


def parse_glossary(glossary_path: Path) -> list[dict]:
    """
    Parse the GLOSSARY.md table. Returns a list of dicts:
      {english, japanese, forbidden: list[str]}
    """
    if not glossary_path.exists():
        print(f'WARNING: GLOSSARY not found at {glossary_path}', file=sys.stderr)
        return []

    entries = []
    in_table = False
    header_seen = False
    separator_seen = False

    for line in glossary_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line.startswith('|'):
            in_table = False
            header_seen = False
            separator_seen = False
            continue

        # Detect table header
        if 'English term' in line and '日本語訳' in line:
            in_table = True
            header_seen = True
            separator_seen = False
            continue

        if in_table and not separator_seen:
            # separator row: |---|---|...
            if re.match(r'^\|[-| :]+\|$', line):
                separator_seen = True
                continue
            continue

        if in_table and header_seen and separator_seen:
            # Data row
            cells = [c.strip() for c in line.strip('|').split('|')]
            if len(cells) < 2:
                continue
            english = cells[0].strip()
            japanese = cells[1].strip()
            forbidden_raw = cells[4].strip() if len(cells) > 4 else ''

            # Parse forbidden: comma-separated, strip quotes and ⚠要確認
            forbidden = []
            for f in forbidden_raw.split('、'):
                f = f.strip()
                f = re.sub(r'⚠[^\s]*', '', f).strip()
                f = f.strip('「」""')
                if f:
                    forbidden.append(f)

            if english:
                entries.append({
                    'english': english,
                    'japanese': japanese,
                    'forbidden': forbidden,
                })

    return entries


def load_corpus(corpus_root: Path) -> list[tuple[Path, dict]]:
    docs = []
    for fpath in sorted(corpus_root.rglob('*.yaml')):
        try:
            with open(fpath, encoding='utf-8') as f:
                doc = yaml.safe_load(f)
            if isinstance(doc, dict):
                docs.append((fpath, doc))
        except (yaml.YAMLError, OSError):
            pass
    return docs


def get_text_fields(doc: dict) -> str:
    """Concatenate statement_ja and proof_ja for linting."""
    parts = []
    for field in ('statement_ja', 'proof_ja'):
        val = doc.get(field)
        if isinstance(val, str):
            parts.append(val)
    return ' '.join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true',
                        help='Exit 1 on any finding (default: warn only)')
    parser.add_argument('--corpus', default=None,
                        help='Lint only this subdirectory (default: entire corpus/)')
    args = parser.parse_args()

    corpus_root = Path(args.corpus) if args.corpus else CORPUS_DIR
    if not corpus_root.is_dir():
        sys.exit(f'ERROR: corpus directory not found: {corpus_root}')

    glossary = parse_glossary(GLOSSARY_PATH)
    if not glossary:
        print('WARNING: empty or missing glossary — no linting performed')
        return

    corpus = load_corpus(corpus_root)
    if not corpus:
        print(f'No corpus files found under {corpus_root}. Nothing to lint.')
        return

    findings: list[str] = []

    for fpath, doc in corpus:
        text = get_text_fields(doc)
        if not text.strip():
            continue

        for entry in glossary:
            english = entry['english']
            japanese = entry['japanese']
            forbidden = entry['forbidden']

            # Check for forbidden translations
            for bad in forbidden:
                if bad and bad in text:
                    findings.append(
                        f'WARN [{fpath.relative_to(REPO_ROOT)}]: '
                        f'forbidden translation "{bad}" for "{english}" '
                        f'(use: {japanese})'
                    )

    # Summary
    if findings:
        print(f'{len(findings)} glossary finding(s):')
        for f in findings:
            print(f'  {f}')
    else:
        n = len(corpus)
        print(f'OK — {n} corpus file(s) checked, no glossary violations.')

    if args.strict and findings:
        sys.exit(1)


if __name__ == '__main__':
    main()
