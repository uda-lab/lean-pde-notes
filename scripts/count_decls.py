#!/usr/bin/env python3
"""
count_decls.py — fallback name-universe generator for lean-pde-notes.

Walks a lean-pde checkout, strips Lean block comments /- ... -/ (nested) and
-- line comments, and extracts declarations matching the attribute-aware pattern:
  ^\\s*(?:@\\[[^\\]]*\\]\\s*)*(?:private\\s+|protected\\s+|noncomputable\\s+|partial\\s+|unsafe\\s+)*
  (theorem|lemma|def|structure|instance|abbrev)\\s+([^\\s({:\\[]+)

Resolves the enclosing `namespace` stack to produce fully-qualified names.

Outputs extracted/names-fallback.json relative to THIS script's parent directory:
  [{"name": ..., "kind": ..., "file": ..., "line": ...}, ...]

Usage:
    python3 scripts/count_decls.py /path/to/lean-pde
    python3 scripts/count_decls.py /path/to/lean-pde --out /custom/path/names.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Comment stripping
# ---------------------------------------------------------------------------

def strip_comments(source: str) -> list[tuple[int, str]]:
    """
    Returns a list of (original_line_number_1indexed, stripped_line) pairs.
    Block comments /- ... -/ (nestable) are replaced with spaces (preserving
    line count).  Inline -- comments are truncated.  String literals are NOT
    specially handled — the vast majority of Lean code has no string literals
    that would confuse the declaration pattern.
    """
    result_chars: list[str] = []
    i = 0
    n = len(source)
    depth = 0  # nesting depth for /- ... -/

    while i < n:
        if depth == 0:
            # Check for block comment open
            if source[i:i+2] == '/-':
                depth += 1
                result_chars.append(' ')
                result_chars.append(' ')
                i += 2
                continue
            # Check for line comment
            if source[i:i+2] == '--':
                # consume until newline
                while i < n and source[i] != '\n':
                    result_chars.append(' ')
                    i += 1
                continue
            result_chars.append(source[i])
            i += 1
        else:
            # Inside block comment
            if source[i:i+2] == '/-':
                depth += 1
                result_chars.append(' ')
                result_chars.append(' ')
                i += 2
                continue
            if source[i:i+2] == '-/':
                depth -= 1
                result_chars.append(' ')
                result_chars.append(' ')
                i += 2
                continue
            # preserve newlines so line numbers are stable
            if source[i] == '\n':
                result_chars.append('\n')
            else:
                result_chars.append(' ')
            i += 1

    stripped = ''.join(result_chars)
    lines = stripped.split('\n')
    return [(lineno + 1, line) for lineno, line in enumerate(lines)]


# ---------------------------------------------------------------------------
# Namespace stack
# ---------------------------------------------------------------------------

NS_OPEN_RE = re.compile(r'^\s*namespace\s+(\S+)')
NS_END_RE = re.compile(r'^\s*end\s+(\S+)?')
SECTION_OPEN_RE = re.compile(r'^\s*section\b')
SECTION_END_RE = re.compile(r'^\s*end\b')


def _update_ns_stack(
    stack: list[str],
    section_depth: list[int],
    line: str,
) -> None:
    """Mutate stack and section_depth in-place based on namespace/end/section."""
    m = NS_OPEN_RE.match(line)
    if m:
        stack.append(m.group(1))
        section_depth.append(0)
        return

    # section (unnamed scope — doesn't add to qualified name)
    sm = SECTION_OPEN_RE.match(line)
    if sm:
        if section_depth:
            section_depth[-1] += 1
        return

    em = NS_END_RE.match(line)
    if em:
        ns_name = em.group(1)
        if ns_name is None:
            # bare `end` — closes innermost section or namespace
            if section_depth and section_depth[-1] > 0:
                section_depth[-1] -= 1
            elif stack:
                stack.pop()
                section_depth.pop() if section_depth else None
        else:
            # named end — find and pop matching namespace
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx] == ns_name:
                    # pop everything down to and including that namespace
                    del stack[idx:]
                    del section_depth[idx:]
                    break


# ---------------------------------------------------------------------------
# Declaration pattern
# ---------------------------------------------------------------------------

DECL_RE = re.compile(
    r'^\s*'
    r'(?:@\[[^\]]*\]\s*)*'
    r'(?:private\s+|protected\s+|noncomputable\s+|partial\s+|unsafe\s+)*'
    r'(theorem|lemma|def|structure|instance|abbrev)\s+'
    r'([^\s({:\[]+)',
)

# Anonymous instance: `instance : SomeType` or `instance (priority := N) : SomeType`
# — the name token is absent, next non-space char is `:` or `(`
ANON_INSTANCE_RE = re.compile(
    r'^\s*'
    r'(?:@\[[^\]]*\]\s*)*'
    r'(?:noncomputable\s+|private\s+|protected\s+)*'
    r'instance\s*(?:\([^)]*\)\s*)?:'
)


def extract_decls(lean_root: Path) -> list[dict]:
    """Walk lean_root for .lean files and extract all declarations."""
    decls: list[dict] = []
    lean_files = sorted(
        p for p in lean_root.rglob('*.lean')
        if '.lake' not in p.parts
    )

    for fpath in lean_files:
        try:
            source = fpath.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue

        rel_path = fpath.relative_to(lean_root)
        stripped_lines = strip_comments(source)

        ns_stack: list[str] = []
        section_depth: list[int] = []

        for lineno, line in stripped_lines:
            # Update namespace tracking
            _update_ns_stack(ns_stack, section_depth, line)

            # Try to match a named declaration
            m = DECL_RE.match(line)
            if m:
                kind = m.group(1)
                simple_name = m.group(2)
                # strip trailing punctuation that might have leaked in
                simple_name = simple_name.rstrip('.:,;')
                if not simple_name:
                    continue
                if ns_stack:
                    full_name = '.'.join(ns_stack) + '.' + simple_name
                else:
                    full_name = simple_name
                decls.append({
                    'name': full_name,
                    'kind': kind,
                    'file': str(rel_path),
                    'line': lineno,
                })
                continue

            # Try anonymous instance (no name before `:`)
            am = ANON_INSTANCE_RE.match(line)
            if am:
                # Synthesize a name as «instance»_<file>_<line> so it is unique
                stem = Path(rel_path).stem.replace('.', '_')
                synthetic = f'«instance»_{stem}_L{lineno}'
                if ns_stack:
                    full_name = '.'.join(ns_stack) + '.' + synthetic
                else:
                    full_name = synthetic
                decls.append({
                    'name': full_name,
                    'kind': 'instance',
                    'file': str(rel_path),
                    'line': lineno,
                    'anonymous': True,
                })

    return decls


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lean_root', help='Path to the lean-pde checkout')
    parser.add_argument(
        '--out',
        default=None,
        help='Output JSON path (default: extracted/names-fallback.json next to scripts/)',
    )
    args = parser.parse_args()

    lean_root = Path(args.lean_root).resolve()
    if not lean_root.is_dir():
        print(f'ERROR: {lean_root} is not a directory', file=sys.stderr)
        sys.exit(1)

    if args.out:
        out_path = Path(args.out)
    else:
        # Default: <repo-root>/extracted/names-fallback.json
        scripts_dir = Path(__file__).parent
        repo_root = scripts_dir.parent
        out_path = repo_root / 'extracted' / 'names-fallback.json'

    decls = extract_decls(lean_root)

    # Print summary
    from collections import Counter
    kind_counts = Counter(d['kind'] for d in decls)
    total = len(decls)
    print(f'Total declarations: {total}')
    for kind in ['theorem', 'def', 'lemma', 'structure', 'instance', 'abbrev']:
        print(f'  {kind}: {kind_counts.get(kind, 0)}')
    other = {k: v for k, v in kind_counts.items()
             if k not in ('theorem', 'def', 'lemma', 'structure', 'instance', 'abbrev')}
    for k, v in sorted(other.items()):
        print(f'  {k}: {v}')

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(decls, f, ensure_ascii=False, indent=2)
    print(f'Written {total} entries to {out_path}')


if __name__ == '__main__':
    main()
