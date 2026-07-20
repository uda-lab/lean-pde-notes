#!/usr/bin/env python3
"""Regression checks for notes#32 scripts/verify_source_provenance.py — the fail-closed
provenance gate for source-enabled site data builds.

Covers each of the four checks (pin match via real `git rev-parse HEAD`, clean/detached
checkout, source_count == decl_count, nodes.json pin == sources.json pin) both passing
and failing, using real temporary git repositories rather than mocking git.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_source_provenance.py"


def import_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_main(module, argv: list[str]) -> tuple[int, str]:
    old_argv = sys.argv[:]
    sys.argv = [str(module.__file__), *argv]
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = module.main()
    finally:
        sys.argv = old_argv
    return code, out.getvalue()


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def make_pinned_repo(tmp: Path) -> tuple[Path, str]:
    """A clean git repo with one commit, checked out with HEAD detached at that commit
    (mirrors an `actions/checkout` at a fixed sha, not a branch checkout)."""
    root = tmp / "lean-root"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test")
    (root / "Foo.lean").write_text("theorem foo : True := trivial\n", encoding="utf-8")
    git(root, "add", "Foo.lean")
    git(root, "commit", "-q", "-m", "init")
    sha = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    git(root, "checkout", "-q", "--detach", sha)
    return root, sha


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def base_args(tmp: Path, lean_root: Path, pin: str, nodes: dict, sources: dict) -> list[str]:
    pin_file = tmp / "PIN"
    pin_file.write_text(pin, encoding="utf-8")
    nodes_path = tmp / "nodes.json"
    sources_path = tmp / "sources.json"
    write_json(nodes_path, nodes)
    write_json(sources_path, sources)
    return [
        "--lean-root", str(lean_root),
        "--pin-file", str(pin_file),
        "--nodes-json", str(nodes_path),
        "--sources-json", str(sources_path),
    ]


def test_all_checks_pass() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_pass")
    lean_root, sha = make_pinned_repo(tmp)
    nodes = {"pin": sha, "source_count": 3, "decl_count": 3}
    sources = {"pin": sha, "source_count": 3}
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 0, out
    assert "pin_match" in out and "PASS" in out
    assert "clean_detached" in out
    assert "source_coverage" in out
    assert "pin_consistency" in out


def test_pin_mismatch_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_pin_mismatch")
    lean_root, sha = make_pinned_repo(tmp)
    nodes = {"pin": sha, "source_count": 1, "decl_count": 1}
    sources = {"pin": sha, "source_count": 1}
    args = base_args(tmp, lean_root, "0" * 40, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "pin_match" in out and "FAIL" in out


def test_dirty_checkout_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_dirty")
    lean_root, sha = make_pinned_repo(tmp)
    (lean_root / "scratch.txt").write_text("leftover build artifact\n", encoding="utf-8")
    nodes = {"pin": sha, "source_count": 1, "decl_count": 1}
    sources = {"pin": sha, "source_count": 1}
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "clean_detached" in out and "FAIL" in out


def test_attached_branch_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_attached")
    lean_root, sha = make_pinned_repo(tmp)
    git(lean_root, "checkout", "-q", "-b", "main")
    nodes = {"pin": sha, "source_count": 1, "decl_count": 1}
    sources = {"pin": sha, "source_count": 1}
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "clean_detached" in out and "FAIL" in out
    assert "detached" in out


def test_source_count_mismatch_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_coverage")
    lean_root, sha = make_pinned_repo(tmp)
    nodes = {"pin": sha, "source_count": 2, "decl_count": 3}
    sources = {"pin": sha, "source_count": 2}
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out


def test_pin_inconsistency_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_pin_consistency")
    lean_root, sha = make_pinned_repo(tmp)
    nodes = {"pin": sha, "source_count": 1, "decl_count": 1}
    sources = {"pin": "f" * 40, "source_count": 1}
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "pin_consistency" in out and "FAIL" in out


def test_stale_matching_pin_pair_fails() -> None:
    """nodes.json and sources.json agree with each other but not with the current
    extracted/PIN — a stale-but-internally-consistent pair from a previous build. This
    must still fail: pin_consistency checks against the PIN file, not just each other."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_stale_pin_pair")
    lean_root, sha = make_pinned_repo(tmp)
    stale_pin = "e" * 40
    nodes = {"pin": stale_pin, "source_count": 1, "decl_count": 1}
    sources = {"pin": stale_pin, "source_count": 1}
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "pin_consistency" in out and "FAIL" in out
    assert "stale" in out


def test_sources_json_source_count_mismatch_fails() -> None:
    """nodes.json's own source_count == decl_count, but sources.json's declared
    source_count disagrees — a stale-but-internally-plausible sources.json."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_sources_count_mismatch")
    lean_root, sha = make_pinned_repo(tmp)
    nodes = {"pin": sha, "source_count": 3, "decl_count": 3}
    sources = {"pin": sha, "source_count": 2}
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out
    assert "different runs" in out


def test_sources_map_entry_count_mismatch_fails() -> None:
    """sources.json's declared source_count matches nodes.json, but the actual "sources"
    object has a different number of entries — an internally inconsistent sources.json."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_sources_map_mismatch")
    lean_root, sha = make_pinned_repo(tmp)
    nodes = {"pin": sha, "source_count": 2, "decl_count": 2}
    sources = {"pin": sha, "source_count": 2, "sources": {"a": "text"}}
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out


def test_missing_lean_root_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_missing_root")
    nodes = {"pin": "a" * 40, "source_count": 1, "decl_count": 1}
    sources = {"pin": "a" * 40, "source_count": 1}
    args = base_args(tmp, tmp / "does-not-exist", "a" * 40, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "does not exist" in out


def main() -> None:
    tests = [
        test_all_checks_pass,
        test_pin_mismatch_fails,
        test_dirty_checkout_fails,
        test_attached_branch_fails,
        test_source_count_mismatch_fails,
        test_pin_inconsistency_fails,
        test_stale_matching_pin_pair_fails,
        test_sources_json_source_count_mismatch_fails,
        test_sources_map_entry_count_mismatch_fails,
        test_missing_lean_root_fails,
    ]
    for test in tests:
        test()
        print(f"  ok  {test.__name__}")
    print(f"\nAll {len(tests)} notes#32 provenance-gate checks passed.")


if __name__ == "__main__":
    main()
