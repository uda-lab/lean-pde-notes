#!/usr/bin/env python3
"""
coverage.py — per-chapter and per-tier coverage table for lean-pde-notes.

Reads the name universe (extracted/decls.json or names-fallback.json) and all
corpus/**/*.yaml files, then computes annotated/total counts per chapter.

Writes site/data/coverage.json and prints a markdown table.

Usage:
    python3 scripts/coverage.py
    python3 scripts/coverage.py --json-only   # skip markdown table
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    sys.exit('ERROR: PyYAML required. pip install pyyaml')

REPO_ROOT = Path(__file__).parent.parent
CORPUS_DIR = REPO_ROOT / 'corpus'
EXTRACTED_DIR = REPO_ROOT / 'extracted'
SITE_DATA_DIR = REPO_ROOT / 'site' / 'data'

CHAPTERS_ORDER = [
    'spaces',
    'projections-galerkin',
    'ode',
    'energy',
    'compactness',
    'limit-passage',
    'capstone-r3',
    'capstone-torus',
    'bochner',
    'misc',
]

CHAPTER_LABELS = {
    'spaces':              '関数空間と基本設定',
    'projections-galerkin': 'Galerkin 射影と基底',
    'ode':                 'Galerkin ODE 系',
    'energy':              'エネルギー恒等式と不等式',
    'compactness':         'コンパクト性（空間・時間）',
    'limit-passage':       '極限移行（非線形項）',
    'capstone-r3':         'R3 主定理',
    'capstone-torus':      'T³ 主定理',
    'bochner':             'Bochner 時間層',
    'misc':                'その他・共通基盤',
}


def load_universe() -> list[dict]:
    decls_path = EXTRACTED_DIR / 'decls.json'
    fallback_path = EXTRACTED_DIR / 'names-fallback.json'
    if decls_path.exists():
        with open(decls_path, encoding='utf-8') as f:
            return json.load(f)
    if fallback_path.exists():
        with open(fallback_path, encoding='utf-8') as f:
            return json.load(f)
    return []


def load_corpus() -> list[dict]:
    docs = []
    for fpath in sorted(CORPUS_DIR.rglob('*.yaml')):
        try:
            with open(fpath, encoding='utf-8') as f:
                doc = yaml.safe_load(f)
            if isinstance(doc, dict) and 'name' in doc:
                docs.append(doc)
        except (yaml.YAMLError, OSError):
            pass
    return docs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json-only', action='store_true')
    args = parser.parse_args()

    universe = load_universe()
    corpus = load_corpus()

    total = len(universe)
    annotated_names = {d['name'] for d in corpus}
    full_names = {d['name'] for d in corpus if d.get('tier') == 'full'}
    gloss_names = {d['name'] for d in corpus if d.get('tier') == 'gloss'}

    # Per-chapter breakdown from corpus
    chapter_annotated: dict[str, int] = {ch: 0 for ch in CHAPTERS_ORDER}
    chapter_full: dict[str, int] = {ch: 0 for ch in CHAPTERS_ORDER}
    chapter_gloss: dict[str, int] = {ch: 0 for ch in CHAPTERS_ORDER}

    for doc in corpus:
        ch = doc.get('chapter', 'misc')
        if ch not in chapter_annotated:
            ch = 'misc'
        chapter_annotated[ch] += 1
        if doc.get('tier') == 'full':
            chapter_full[ch] += 1
        elif doc.get('tier') == 'gloss':
            chapter_gloss[ch] += 1

    # Build coverage JSON
    coverage = {
        'total_decls': total,
        'annotated': len(annotated_names),
        'full': len(full_names),
        'gloss': len(gloss_names),
        'unannotated': total - len(annotated_names),
        'pct_annotated': round(100 * len(annotated_names) / total, 1) if total else 0,
        'chapters': {
            ch: {
                'label_ja': CHAPTER_LABELS.get(ch, ch),
                'annotated': chapter_annotated[ch],
                'full': chapter_full[ch],
                'gloss': chapter_gloss[ch],
            }
            for ch in CHAPTERS_ORDER
        },
    }

    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SITE_DATA_DIR / 'coverage.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(coverage, f, ensure_ascii=False, indent=2)
    print(f'Wrote {out_path}')

    if args.json_only:
        return

    # Print markdown table
    print()
    print(f'## Coverage: {len(annotated_names)}/{total} ({coverage["pct_annotated"]}%) annotated')
    print()
    print(f'| Chapter | Label | Annotated | full | gloss |')
    print(f'|---------|-------|----------:|-----:|------:|')
    for ch in CHAPTERS_ORDER:
        label = CHAPTER_LABELS.get(ch, ch)
        ann = chapter_annotated[ch]
        full = chapter_full[ch]
        gloss = chapter_gloss[ch]
        print(f'| `{ch}` | {label} | {ann} | {full} | {gloss} |')
    print()
    print(f'| **Total** | | **{len(annotated_names)}** | **{len(full_names)}** | **{len(gloss_names)}** |')
    print()
    print(f'Universe: {total} declarations (from {"decls.json" if (EXTRACTED_DIR / "decls.json").exists() else "names-fallback.json"})')


if __name__ == '__main__':
    main()
