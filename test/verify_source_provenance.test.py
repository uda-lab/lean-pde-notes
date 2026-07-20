#!/usr/bin/env python3
"""Regression checks for notes#32 scripts/verify_source_provenance.py — the fail-closed
provenance gate for source-enabled site data builds.

Covers each check (pin match via real `git rev-parse HEAD`, clean/detached checkout,
source_count == decl_count cross-checked against sources.json's own count/entries/slug
set, and nodes.json pin == sources.json pin == extracted/PIN) both passing and failing,
using real temporary git repositories rather than mocking git.

PR #114 owner + copilot review (2026-07-20) found that an earlier version of
check_source_coverage() was fail-open: it only validated sources.json's "sources" object
when that field happened to already be a dict, so a missing/non-object "sources" field
passed as long as the declared counts matched, and test_all_checks_pass()'s own fixture
omitted "sources" and "nodes" arrays entirely. Every fixture below now carries the full
realistic build_site_data.py output shape (a "nodes" list and a "sources" map with
exactly source_count entries), and each failure-mode test mutates exactly one field away
from that valid baseline — so a test can't accidentally pass for the wrong reason.
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


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def make_payloads(sha: str, decl_count: int, source_count: int) -> tuple[dict, dict]:
    """A valid, internally-consistent (nodes.json, sources.json) pair reflecting the real
    build_site_data.py output shape: the first `source_count` of `decl_count` node slugs
    are marked has_source:true and have a matching entry in sources.json's "sources" map."""
    node_list = [
        {"slug": f"decl{i}", "has_source": i < source_count}
        for i in range(decl_count)
    ]
    nodes = {
        "pin": sha,
        "source_count": source_count,
        "decl_count": decl_count,
        "nodes": node_list,
    }
    sources_map = {f"decl{i}": f"source text {i}" for i in range(source_count)}
    sources = {
        "pin": sha,
        "source_count": source_count,
        "sources": sources_map,
    }
    return nodes, sources


def base_args(tmp: Path, lean_root: Path, pin: str, nodes, sources) -> list[str]:
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
    nodes, sources = make_payloads(sha, decl_count=3, source_count=3)
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
    nodes, sources = make_payloads(sha, decl_count=1, source_count=1)
    args = base_args(tmp, lean_root, "0" * 40, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "pin_match" in out and "FAIL" in out


def test_dirty_checkout_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_dirty")
    lean_root, sha = make_pinned_repo(tmp)
    (lean_root / "scratch.txt").write_text("leftover build artifact\n", encoding="utf-8")
    nodes, sources = make_payloads(sha, decl_count=1, source_count=1)
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "clean_detached" in out and "FAIL" in out


def test_attached_branch_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_attached")
    lean_root, sha = make_pinned_repo(tmp)
    git(lean_root, "checkout", "-q", "-b", "main")
    nodes, sources = make_payloads(sha, decl_count=1, source_count=1)
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "clean_detached" in out and "FAIL" in out
    assert "detached" in out


def test_source_count_mismatch_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_coverage")
    lean_root, sha = make_pinned_repo(tmp)
    nodes, sources = make_payloads(sha, decl_count=3, source_count=2)
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out
    assert "-1 declaration" not in out  # never a negative miss count


def test_source_count_exceeds_decl_count_fails_with_clear_message() -> None:
    """source_count > decl_count is impossible for a real build; must be its own failure
    message, not a nonsensical negative "misses" count (copilot review, PR #114)."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_source_exceeds_decl")
    lean_root, sha = make_pinned_repo(tmp)
    nodes, sources = make_payloads(sha, decl_count=2, source_count=2)
    nodes["source_count"] = 3  # now exceeds decl_count=2, with no matching sources.json change
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out
    assert "exceeds decl_count" in out
    assert "-1 declaration" not in out


def test_pin_inconsistency_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_pin_consistency")
    lean_root, sha = make_pinned_repo(tmp)
    nodes, sources = make_payloads(sha, decl_count=1, source_count=1)
    sources["pin"] = "f" * 40
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
    nodes, sources = make_payloads(stale_pin, decl_count=1, source_count=1)
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
    nodes, sources = make_payloads(sha, decl_count=3, source_count=3)
    sources["source_count"] = 2
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
    nodes, sources = make_payloads(sha, decl_count=2, source_count=2)
    sources["sources"] = {"decl0": "text"}  # one entry, but source_count still says 2
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out


def test_sources_field_missing_fails() -> None:
    """sources.json omits the "sources" object entirely — must fail closed, not pass just
    because the declared counts happen to agree (the exact fail-open gap PR #114 review
    found: an isinstance(..., dict) guard silently skipped this case)."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_sources_field_missing")
    lean_root, sha = make_pinned_repo(tmp)
    nodes, sources = make_payloads(sha, decl_count=2, source_count=2)
    del sources["sources"]
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out
    assert "missing or not a JSON object" in out


def test_sources_field_wrong_type_fails() -> None:
    """sources.json's "sources" field is present but is a list, not an object."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_sources_field_wrong_type")
    lean_root, sha = make_pinned_repo(tmp)
    nodes, sources = make_payloads(sha, decl_count=2, source_count=2)
    sources["sources"] = ["text0", "text1"]
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out
    assert "missing or not a JSON object" in out


def test_nodes_field_missing_fails() -> None:
    """nodes.json omits the "nodes" array entirely."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_nodes_field_missing")
    lean_root, sha = make_pinned_repo(tmp)
    nodes, sources = make_payloads(sha, decl_count=2, source_count=2)
    del nodes["nodes"]
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out
    assert '"nodes" field is missing or not a list' in out


def test_nodes_array_length_mismatch_fails() -> None:
    """nodes.json declares decl_count=3 but its "nodes" array only has 2 entries."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_nodes_length_mismatch")
    lean_root, sha = make_pinned_repo(tmp)
    nodes, sources = make_payloads(sha, decl_count=3, source_count=3)
    nodes["nodes"] = nodes["nodes"][:2]
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out
    assert '"nodes" array has 2 entries' in out


def test_has_source_slug_set_mismatch_fails() -> None:
    """The set of node slugs marked has_source:true does not match sources.json's key
    set, even though every count lines up — e.g. a declaration was renamed between the
    nodes.json and sources.json halves of a build."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_slug_mismatch")
    lean_root, sha = make_pinned_repo(tmp)
    nodes, sources = make_payloads(sha, decl_count=2, source_count=2)
    sources["sources"] = {"decl0": "text", "declRenamed": "text"}  # same count, different keys
    args = base_args(tmp, lean_root, sha, nodes, sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "source_coverage" in out and "FAIL" in out
    assert "does not match" in out


def test_nodes_json_non_object_top_level_fails() -> None:
    """nodes.json is valid JSON but its top-level value is a list, not an object —
    load_json() must reject this explicitly rather than crash later on .get() (copilot
    review, PR #114)."""
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_nodes_non_object")
    lean_root, sha = make_pinned_repo(tmp)
    _, sources = make_payloads(sha, decl_count=1, source_count=1)
    args = base_args(tmp, lean_root, sha, ["not", "an", "object"], sources)

    code, out = run_main(module, args)
    assert code == 1, out
    assert "expected a JSON object at the top level" in out


def test_missing_lean_root_fails() -> None:
    tmp = Path(tempfile.mkdtemp())
    module = import_script("verify_missing_root")
    nodes, sources = make_payloads("a" * 40, decl_count=1, source_count=1)
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
        test_source_count_exceeds_decl_count_fails_with_clear_message,
        test_pin_inconsistency_fails,
        test_stale_matching_pin_pair_fails,
        test_sources_json_source_count_mismatch_fails,
        test_sources_map_entry_count_mismatch_fails,
        test_sources_field_missing_fails,
        test_sources_field_wrong_type_fails,
        test_nodes_field_missing_fails,
        test_nodes_array_length_mismatch_fails,
        test_has_source_slug_set_mismatch_fails,
        test_nodes_json_non_object_top_level_fails,
        test_missing_lean_root_fails,
    ]
    for test in tests:
        test()
        print(f"  ok  {test.__name__}")
    print(f"\nAll {len(tests)} notes#32 provenance-gate checks passed.")


if __name__ == "__main__":
    main()
