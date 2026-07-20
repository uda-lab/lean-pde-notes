#!/usr/bin/env python3
"""
verify_source_provenance.py — fail-closed provenance gate for source-enabled
site data builds (notes#32 "Audit-mandated provenance additions").

This script is the independent check that a source-enabled `build_site_data.py
--lean-root <path>` run actually embedded verbatim text from the exact,
untampered `extracted/PIN` commit — rather than the workflow (or a caller)
merely asserting that `--lean-root` points at the right place. It re-derives
every fact from disk and from `git` plumbing in the checkout itself; it does
not trust any caller-supplied claim about what the checkout is.

Checks (see notes#32 issue body, "Audit-mandated provenance additions"):

  1. `git rev-parse HEAD` inside --lean-root is byte-for-byte equal to the PIN
     read directly from --pin-file. This also covers "the builder does not
     merely trust the operator-supplied --lean-root": the equality is derived
     from git plumbing run against the checkout's actual `.git` state, not
     from a path string, a step output, or an environment variable that some
     earlier workflow step could have set incorrectly.
  2. The checkout is clean (`git status --porcelain` empty) and HEAD is
     detached (not a movable branch ref) — i.e. it is exactly the pinned
     commit, with nothing built, added, or left over from a previous run,
     and not accidentally tracking a branch pointer that could later move.
  3. `source_count == decl_count` and there are zero source-extraction
     misses. `build_site_data.py` records `source_count` as the number of
     declarations for which `SourceReader.source_for()` actually found the
     verbatim text; when a `--lean-root` build attempted extraction for every
     declaration in the universe (`decl_count`), equality of the two implies
     zero misses (hits + misses == decl_count).
  4. `nodes.json`'s embedded `pin` field equals `sources.json`'s embedded
     `pin` field, so the two payloads the frontend joins at runtime cannot
     silently drift apart.

Usage:
    python3 scripts/verify_source_provenance.py --lean-root /path/to/leray-hopf
    python3 scripts/verify_source_provenance.py \\
        --lean-root /path/to/leray-hopf --pin-file extracted/PIN \\
        --nodes-json site/data/nodes.json --sources-json site/data/sources.json

Exits non-zero (fail closed) and prints every violated check if any check
fails; exits 0 and prints a PASS line per check otherwise.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def run_git(lean_root: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ['git', '-C', str(lean_root), *args],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def check_pin_match(lean_root: Path, pin: str, failures: list[str], passes: list[str]) -> None:
    code, out, err = run_git(lean_root, 'rev-parse', 'HEAD')
    if code != 0:
        failures.append(
            f'pin_match: `git -C {lean_root} rev-parse HEAD` failed (not a git '
            f'checkout, or --lean-root is wrong): {err or out}'
        )
        return
    head = out
    if head != pin:
        failures.append(
            f'pin_match: --lean-root HEAD ({head}) does not equal extracted/PIN ({pin})'
        )
        return
    passes.append(f'pin_match: --lean-root HEAD == PIN ({pin})')


def check_clean_detached(lean_root: Path, failures: list[str], passes: list[str]) -> None:
    code, out, err = run_git(lean_root, 'status', '--porcelain')
    if code != 0:
        failures.append(
            f'clean_detached: `git -C {lean_root} status --porcelain` failed: {err or out}'
        )
        return
    if out:
        failures.append(
            f'clean_detached: --lean-root checkout is not clean; git status --porcelain '
            f'reported:\n{out}'
        )
        return

    code, out, err = run_git(lean_root, 'symbolic-ref', '-q', 'HEAD')
    if code == 0:
        failures.append(
            f'clean_detached: --lean-root HEAD is attached to a branch ({out}), not '
            f'detached at a fixed commit; the checkout could move underneath the build'
        )
        return
    passes.append('clean_detached: --lean-root checkout is clean and HEAD is detached')


def check_source_coverage(nodes: dict, sources: dict, failures: list[str], passes: list[str]) -> None:
    """source_count == decl_count (zero misses), cross-checked against sources.json's own
    declared count and its actual entry count — so a stale sources.json paired with a
    fresh nodes.json (or vice versa) is caught here rather than only in pin_consistency."""
    source_count = nodes.get('source_count')
    decl_count = nodes.get('decl_count')
    if source_count is None or decl_count is None:
        failures.append(
            'source_coverage: nodes.json is missing source_count and/or decl_count'
        )
        return
    if source_count != decl_count:
        misses = decl_count - source_count
        failures.append(
            f'source_coverage: source_count ({source_count}) != decl_count '
            f'({decl_count}) — {misses} declaration(s) had no readable source range; '
            f're-run build_site_data.py --lean-root and inspect its '
            f'"records had no readable source range" warning'
        )
        return

    sources_source_count = sources.get('source_count')
    if sources_source_count is None:
        failures.append('source_coverage: sources.json is missing source_count')
        return
    if source_count != sources_source_count:
        failures.append(
            f'source_coverage: nodes.json source_count ({source_count}) != sources.json '
            f'source_count ({sources_source_count}) — the two payloads were built from '
            f'different runs and do not agree'
        )
        return

    sources_map = sources.get('sources')
    if isinstance(sources_map, dict) and len(sources_map) != sources_source_count:
        failures.append(
            f'source_coverage: sources.json declares source_count={sources_source_count} '
            f'but its "sources" object has {len(sources_map)} entries'
        )
        return

    passes.append(
        f'source_coverage: source_count == decl_count == sources.json source_count == '
        f'{decl_count} (zero misses, cross-checked against sources.json)'
    )


def check_pin_consistency(pin: str, nodes: dict, sources: dict, failures: list[str], passes: list[str]) -> None:
    """nodes.json pin and sources.json pin must both equal the PIN this build was run
    for — not merely equal each other, which a stale-but-matching pair from a previous
    run could also satisfy."""
    nodes_pin = nodes.get('pin')
    sources_pin = sources.get('pin')
    if not nodes_pin or not sources_pin:
        failures.append(
            f'pin_consistency: missing pin field(s) — nodes.json pin={nodes_pin!r}, '
            f'sources.json pin={sources_pin!r}'
        )
        return
    if nodes_pin != pin:
        failures.append(
            f'pin_consistency: nodes.json pin ({nodes_pin}) != extracted/PIN ({pin}) — '
            f'nodes.json appears to be stale'
        )
        return
    if sources_pin != pin:
        failures.append(
            f'pin_consistency: sources.json pin ({sources_pin}) != extracted/PIN ({pin}) '
            f'— sources.json appears to be stale'
        )
        return
    passes.append(f'pin_consistency: nodes.json pin == sources.json pin == extracted/PIN ({pin})')


def load_json(path: Path, label: str, failures: list[str]) -> dict | None:
    if not path.is_file():
        failures.append(f'{label}: file not found: {path}')
        return None
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        failures.append(f'{label}: invalid JSON in {path}: {exc}')
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--lean-root', required=True,
                        help='Path to the leray-hopf checkout used for the source-enabled build')
    parser.add_argument('--pin-file', default=str(REPO_ROOT / 'extracted' / 'PIN'),
                        help='Path to extracted/PIN (default: %(default)s)')
    parser.add_argument('--nodes-json', default=str(REPO_ROOT / 'site' / 'data' / 'nodes.json'),
                        help='Path to the built nodes.json (default: %(default)s)')
    parser.add_argument('--sources-json', default=str(REPO_ROOT / 'site' / 'data' / 'sources.json'),
                        help='Path to the built sources.json (default: %(default)s)')
    args = parser.parse_args()

    lean_root = Path(args.lean_root)
    pin_file = Path(args.pin_file)
    nodes_path = Path(args.nodes_json)
    sources_path = Path(args.sources_json)

    failures: list[str] = []
    passes: list[str] = []

    pin: str | None = None
    if not pin_file.is_file():
        failures.append(f'pin_match: PIN file not found: {pin_file}')
    else:
        pin = pin_file.read_text(encoding='utf-8').strip()
        if not pin:
            failures.append(f'pin_match: PIN file is empty: {pin_file}')
            pin = None

    if not lean_root.is_dir():
        failures.append(f'pin_match: --lean-root does not exist or is not a directory: {lean_root}')
    else:
        if pin is not None:
            check_pin_match(lean_root, pin, failures, passes)
        check_clean_detached(lean_root, failures, passes)

    nodes = load_json(nodes_path, 'source_coverage/pin_consistency (nodes.json)', failures)
    sources = load_json(sources_path, 'source_coverage/pin_consistency (sources.json)', failures)

    if nodes is not None and sources is not None:
        check_source_coverage(nodes, sources, failures, passes)
        if pin is not None:
            check_pin_consistency(pin, nodes, sources, failures, passes)

    for p in passes:
        print(f'PASS: {p}')

    if failures:
        print(f'\n{len(failures)} provenance check(s) FAILED:', file=sys.stderr)
        for f in failures:
            print(f'  FAIL: {f}', file=sys.stderr)
        return 1

    print(f'\nAll {len(passes)} provenance checks passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
