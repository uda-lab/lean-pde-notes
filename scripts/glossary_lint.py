#!/usr/bin/env python3
"""
glossary_lint.py — corpus translation linter for leray-hopf-notes.

Uses scripts/glossary.py to parse docs/GLOSSARY.md (Markdown table with columns:
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
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    sys.exit('ERROR: PyYAML required. pip install pyyaml')

sys.path.insert(0, str(Path(__file__).parent))
from glossary import parse_glossary  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
GLOSSARY_PATH = REPO_ROOT / 'docs' / 'GLOSSARY.md'
CORPUS_DIR = REPO_ROOT / 'corpus'


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
