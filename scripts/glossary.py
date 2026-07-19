#!/usr/bin/env python3
"""
glossary.py — shared parser for docs/GLOSSARY.md.

Parses the Markdown table (columns: English term | 日本語訳 | Lean 識別子例 | 備考 |
forbidden) into a list of dicts: {english, japanese, note, forbidden: list[str]}.

Used by:
  - scripts/glossary_lint.py: flags forbidden translations and vocabulary drift in
    corpus statement_ja/proof_ja.
  - scripts/build_site_data.py: embeds the parsed table into site/data/nodes.json so
    the static site's search can match glossary terms (notes#73 slice 2) without
    shipping docs/GLOSSARY.md itself.

Standalone usage:
    python3 scripts/glossary.py            # print parsed entries
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GLOSSARY_PATH = REPO_ROOT / 'docs' / 'GLOSSARY.md'


def parse_glossary(glossary_path: Path | None = None) -> list[dict]:
    """
    Parse the GLOSSARY.md table. Returns a list of dicts:
      {english, japanese, note, forbidden: list[str]}
    """
    p = glossary_path or GLOSSARY_PATH
    if not p.exists():
        print(f'WARNING: GLOSSARY not found at {p}', file=sys.stderr)
        return []

    entries = []
    in_table = False
    header_seen = False
    separator_seen = False

    for line in p.read_text(encoding='utf-8').splitlines():
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
            note = cells[3].strip() if len(cells) > 3 else ''
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
                    'note': note,
                    'forbidden': forbidden,
                })

    return entries


if __name__ == '__main__':
    for entry in parse_glossary():
        print(f'{entry["english"]} — {entry["japanese"]}')
