#!/usr/bin/env python3
"""
decl_diff.py — classify declaration changes between two extracted decls.json snapshots.

Compares an OLD and a NEW extraction of the leray-hopf declaration universe and
buckets every declaration into:

  added               present only in NEW
  removed             present only in OLD
  moved               same name, different file (qualified names survive file moves)
  visibility_changed  private flag flipped (private→public promotions and demotions)
  signature_changed   same name+file, signature text differs (informational)

Matching strategy: declarations are joined by fully-qualified display name.
Exact (name, file) pairs match first; the remainder match by name alone when the
name is unambiguous on both sides (detects file moves, including private lemmas
whose `id` is rewritten by a move). Names that stay ambiguous after both passes
are reported in `ambiguous` rather than silently classified.

Typical use during a re-pin:
    git show HEAD:extracted/decls.json > /tmp/decls-old.json
    python3 scripts/decl_diff.py /tmp/decls-old.json extracted/decls.json \
        --markdown /tmp/decl-diff.md

Usage:
    python3 scripts/decl_diff.py OLD.json NEW.json [--json OUT.json] [--markdown OUT.md]
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load(path: Path) -> list[dict]:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        sys.exit(f'ERROR: {path}: expected a JSON array of declaration records')
    return data


def brief(d: dict) -> dict:
    return {
        'name': d['name'],
        'kind': d.get('kind', ''),
        'file': d.get('file', ''),
        'private': bool(d.get('private', False)),
        'startLine': d.get('startLine'),
    }


def diff(old: list[dict], new: list[dict]) -> dict:
    old_by_key = {(d['name'], d.get('file', '')): d for d in old}
    new_by_key = {(d['name'], d.get('file', '')): d for d in new}

    matched: list[tuple[dict, dict]] = []
    old_rest: list[dict] = []
    new_rest: list[dict] = []

    # Pass 1: exact (name, file) matches.
    for key, d in old_by_key.items():
        if key in new_by_key:
            matched.append((d, new_by_key[key]))
        else:
            old_rest.append(d)
    matched_new_keys = {(n['name'], n.get('file', '')) for _, n in matched}
    new_rest = [d for key, d in new_by_key.items() if key not in matched_new_keys]

    # Pass 2: match leftovers by name when unambiguous on both sides (file moves).
    old_by_name: dict[str, list[dict]] = defaultdict(list)
    new_by_name: dict[str, list[dict]] = defaultdict(list)
    for d in old_rest:
        old_by_name[d['name']].append(d)
    for d in new_rest:
        new_by_name[d['name']].append(d)

    moved: list[dict] = []
    ambiguous: list[dict] = []
    removed: list[dict] = []
    added: list[dict] = []

    for name, olds in old_by_name.items():
        news = new_by_name.get(name, [])
        if len(olds) == 1 and len(news) == 1:
            matched.append((olds[0], news[0]))
            moved.append({
                'name': name,
                'kind': news[0].get('kind', ''),
                'old_file': olds[0].get('file', ''),
                'new_file': news[0].get('file', ''),
                'private': bool(news[0].get('private', False)),
            })
        elif not news:
            removed.extend(brief(d) for d in olds)
        else:
            ambiguous.extend({**brief(d), 'side': 'old'} for d in olds)
            ambiguous.extend({**brief(d), 'side': 'new'} for d in news)
    for name, news in new_by_name.items():
        if name not in old_by_name:
            added.extend(brief(d) for d in news)

    visibility_changed: list[dict] = []
    signature_changed: list[dict] = []
    for o, n in matched:
        if bool(o.get('private', False)) != bool(n.get('private', False)):
            visibility_changed.append({
                'name': n['name'],
                'kind': n.get('kind', ''),
                'file': n.get('file', ''),
                'change': 'private→public' if o.get('private') else 'public→private',
            })
        if o.get('signature', '') != n.get('signature', ''):
            signature_changed.append({
                'name': n['name'],
                'kind': n.get('kind', ''),
                'file': n.get('file', ''),
            })

    def order(rows: list[dict], *keys: str) -> list[dict]:
        return sorted(rows, key=lambda r: tuple(r.get(k, '') or '' for k in keys))

    return {
        'counts': {
            'old_total': len(old),
            'new_total': len(new),
            'added': len(added),
            'removed': len(removed),
            'moved': len(moved),
            'visibility_changed': len(visibility_changed),
            'signature_changed': len(signature_changed),
            'ambiguous': len(ambiguous),
        },
        'added': order(added, 'file', 'name'),
        'removed': order(removed, 'file', 'name'),
        'moved': order(moved, 'new_file', 'name'),
        'visibility_changed': order(visibility_changed, 'change', 'file', 'name'),
        'signature_changed': order(signature_changed, 'file', 'name'),
        'ambiguous': order(ambiguous, 'name', 'side', 'file'),
    }


def to_markdown(result: dict) -> str:
    c = result['counts']
    lines = [
        '# Declaration diff',
        '',
        f"old: {c['old_total']} decls / new: {c['new_total']} decls",
        '',
        f"| bucket | count |",
        f"|---|---|",
    ]
    for bucket in ('added', 'removed', 'moved', 'visibility_changed',
                   'signature_changed', 'ambiguous'):
        lines.append(f"| {bucket} | {c[bucket]} |")

    def vis(row: dict) -> str:
        return 'private' if row.get('private') else 'public'

    if result['removed']:
        lines += ['', '## Removed', '']
        for r in result['removed']:
            lines.append(f"- `{r['name']}` ({vis(r)} {r['kind']}) — {r['file']}")
    if result['added']:
        lines += ['', '## Added', '']
        for r in result['added']:
            lines.append(f"- `{r['name']}` ({vis(r)} {r['kind']}) — {r['file']}")
    if result['moved']:
        lines += ['', '## Moved (same name, file changed)', '']
        for r in result['moved']:
            lines.append(f"- `{r['name']}` ({vis(r)} {r['kind']}): {r['old_file']} → {r['new_file']}")
    if result['visibility_changed']:
        lines += ['', '## Visibility changed', '']
        for r in result['visibility_changed']:
            lines.append(f"- `{r['name']}` ({r['kind']}, {r['file']}): {r['change']}")
    if result['signature_changed']:
        lines += ['', '## Signature text changed (informational)', '']
        for r in result['signature_changed']:
            lines.append(f"- `{r['name']}` ({r['kind']}) — {r['file']}")
    if result['ambiguous']:
        lines += ['', '## Ambiguous (manual review required)', '']
        for r in result['ambiguous']:
            lines.append(f"- [{r['side']}] `{r['name']}` ({vis(r)} {r['kind']}) — {r['file']}:{r.get('startLine')}")
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('old', type=Path, help='OLD decls.json')
    parser.add_argument('new', type=Path, help='NEW decls.json')
    parser.add_argument('--json', type=Path, help='write full result as JSON')
    parser.add_argument('--markdown', type=Path, help='write summary as markdown')
    args = parser.parse_args()

    result = diff(load(args.old), load(args.new))

    c = result['counts']
    print(f"old {c['old_total']} → new {c['new_total']}: "
          f"+{c['added']} added, -{c['removed']} removed, {c['moved']} moved, "
          f"{c['visibility_changed']} visibility, {c['signature_changed']} signature, "
          f"{c['ambiguous']} ambiguous")

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
        print(f'wrote {args.json}')
    if args.markdown:
        args.markdown.write_text(to_markdown(result), encoding='utf-8')
        print(f'wrote {args.markdown}')

    if c['ambiguous']:
        print(f"WARNING: {c['ambiguous']} ambiguous records need manual review", file=sys.stderr)


if __name__ == '__main__':
    main()
