#!/usr/bin/env python3
"""
check_docs.py — cheap doc-staleness guard for leray-hopf-notes (notes#71).

leray-hopf-notes went stale before: root README claimed "1,413 declarations" and site/README
claimed "1,412" while the actual extracted universe had already moved to 1,349, then 1,339;
a collision count of "8 groups / 16 decls" lingered long after cleanup left only 2/4. Those
numbers are *generated facts* (from extracted/decls.json), not editorial content, so hand-
maintained prose in "living" docs (docs that describe the *current* pipeline/state) should
never embed them as a literal digit — it should point at the generator instead
(`extracted/decls.json`, `scripts/coverage.py`, `scripts/build_site_data.py` — the latter
prints "Collision groups: N (M decls)" and is the actual source of the collision count;
`scripts/validate.py` uses collisions internally but does not print a summary count).

This script does NOT try to recompute "the right number" and diff it against prose (too
fragile — reformats, footnotes, and legitimate small numbers like "2 capstones" would false-
positive constantly). Instead it enforces the structural fix: living docs must not contain a
declaration/collision-count-shaped number at all. Historical/migration logs are exempt by
design — they are dated snapshots and are expected to carry point-in-time numbers.

Usage:
    python3 scripts/check_docs.py
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# "Living" docs: describe the *current* pipeline/repo state. A declaration/collision count
# embedded here as a literal digit is exactly the notes#71 failure mode.
LIVING_DOCS = [
    REPO_ROOT / 'README.md',
    REPO_ROOT / 'site' / 'README.md',
    REPO_ROOT / 'extracted' / 'README.md',
]

# Historical/dated records are expected to carry point-in-time counts (e.g. "1,412 → 1,347"
# migration deltas) and are exempt.
EXEMPT_DOCS = {
    REPO_ROOT / 'docs' / 'migration-2026-07-refactor.md',
    REPO_ROOT / 'docs' / 'archive' / 'seed-migration-mapping.md',
}

# A number — comma-grouped ("1,339") or a bare 2+ digit integer ("1339") — followed within
# up to 2 intervening words (e.g. "1,339 total declarations") by a declaration/collision-
# count noun, in either language. The bare-integer form matters: generated UI text already
# renders the live count unseparated (e.g. site/app.js's decl_count), so a future stale-count
# edit is just as likely to be spelled "1339 declarations" as "1,339 declarations" — codex
# caught that the comma-grouping-only version let the former slip through undetected.
# Deliberately narrow otherwise: the noun whitelist keeps this from firing on unrelated
# numbers (line numbers, PIN hex, schema draft version, "2 capstones", …).
COUNT_PATTERN = re.compile(
    r'\d{1,3}(?:[,.]\d{3})+(?:\s+\S+){0,2}\s*(?:件|宣言|declarations?|decls?|records?|groups?|entries)'
    r'|\d{2,}(?:\s+\S+){0,2}\s*(?:件|宣言|declarations?|decls?|records?|groups?|entries)'
    r'|\d+\s*(?:groups?|組)\s*/\s*\d+\s*(?:decls?|records?|宣言)',
    re.IGNORECASE,
)


def main() -> None:
    findings: list[str] = []

    for path in LIVING_DOCS:
        if path in EXEMPT_DOCS or not path.is_file():
            continue
        text = path.read_text(encoding='utf-8')
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in COUNT_PATTERN.finditer(line):
                findings.append(
                    f'{path.relative_to(REPO_ROOT)}:{lineno}: hard-coded count-shaped '
                    f'literal "{m.group(0)}" — point at a generator instead '
                    f'(extracted/decls.json, scripts/coverage.py, scripts/build_site_data.py), '
                    f'do not embed the digit in prose (notes#71)'
                )

    if findings:
        print(f'{len(findings)} doc staleness finding(s):')
        for f in findings:
            print(f'  ERROR {f}')
        sys.exit(1)

    print(f'OK — {len(LIVING_DOCS)} living doc(s) checked, no hard-coded declaration/'
          f'collision counts found.')


if __name__ == '__main__':
    main()
