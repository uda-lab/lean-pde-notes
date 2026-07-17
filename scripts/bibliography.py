#!/usr/bin/env python3
"""
bibliography.py — shared parser for docs/bibliography.md.

Parses the `### `citation-id`` headings in docs/bibliography.md into a dict of
{id: {"citation": <first paragraph after the heading>, "line": <heading line number>}}.

Used by:
  - scripts/validate.py: cross-checks corpus `references[].id` against known ids.
  - scripts/build_site_data.py: embeds a resolved id -> citation-text map into
    site/data/nodes.json so the static site can render full citations without
    shipping docs/bibliography.md itself.

Standalone usage:
    python3 scripts/bibliography.py            # print parsed ids
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BIBLIOGRAPHY_PATH = REPO_ROOT / 'docs' / 'bibliography.md'

ID_PATTERN = re.compile(r'^[a-z][a-z0-9-]*$')
HEADING_RE = re.compile(r'^### `([a-z][a-z0-9-]*)`\s*$')


def parse_bibliography(path: Path | None = None) -> dict[str, dict[str, str]]:
    """Return {id: {"citation": str, "line": int}} parsed from docs/bibliography.md.

    "citation" is the first non-empty paragraph after the `### `id`` heading (the
    bibliographic entry itself, before any commentary paragraphs) with Markdown
    emphasis markers (`*`/`_`) stripped for plain-text display.
    """
    p = path or BIBLIOGRAPHY_PATH
    if not p.exists():
        return {}
    lines = p.read_text(encoding='utf-8').splitlines()
    entries: dict[str, dict[str, str]] = {}
    i = 0
    while i < len(lines):
        m = HEADING_RE.match(lines[i])
        if not m:
            i += 1
            continue
        cid = m.group(1)
        heading_line = i + 1  # 1-based
        i += 1
        # Skip blank lines, then collect the first paragraph (until a blank line
        # or the next heading).
        while i < len(lines) and not lines[i].strip():
            i += 1
        para_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith('#'):
            para_lines.append(lines[i])
            i += 1
        citation = ' '.join(para_lines).strip()
        citation = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', citation)  # md link -> "text (url)"
        citation = re.sub(r'[*_]{1,2}', '', citation)
        entries[cid] = {'citation': citation, 'line': heading_line}
    return entries


if __name__ == '__main__':
    for cid, info in sorted(parse_bibliography().items()):
        print(f'{cid} (line {info["line"]}): {info["citation"][:100]}')
