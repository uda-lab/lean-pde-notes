#!/usr/bin/env python3
"""Regression checks for notes#29 scripts/site_data_size_report.py CLI contract.

Covers: default warn-only exit code (even over the warning threshold), the opt-in
--fail-raw-mib/--fail-gzip-mib hard ceiling below/at/above the boundary, and rejection
of invalid ceiling values (non-positive, non-finite including NaN, non-numeric).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "site_data_size_report.py"
MIB = 1024 * 1024


def import_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
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
            try:
                module.main()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
            else:
                code = 0
    finally:
        sys.argv = old_argv
    return code, out.getvalue()


def load_fresh(name: str, root: Path):
    """Import a fresh module instance (so per-test WARN_*/SITE_DATA_DIR patches don't
    leak across tests) and point it at an isolated site/data directory."""
    module = import_script(name, SCRIPT_PATH)
    module.SITE_DATA_DIR = root / "site" / "data"
    return module


def write_nodes_json(path: Path, raw_bytes: int) -> None:
    """Write a valid nodes.json ({"nodes": [], "pad": "A"*k}) whose encoded byte count
    is exactly `raw_bytes`. Padding uses only unescaped ASCII 'A' characters, each one
    UTF-8 byte, so the encoded length is exactly the base length plus the pad length."""
    path.parent.mkdir(parents=True, exist_ok=True)
    base_len = len(json.dumps({"nodes": [], "pad": ""}).encode("utf-8"))
    if raw_bytes < base_len:
        raise ValueError(f"raw_bytes={raw_bytes} is below the minimum of {base_len}")
    content = json.dumps({"nodes": [], "pad": "A" * (raw_bytes - base_len)})
    assert len(content.encode("utf-8")) == raw_bytes
    path.write_text(content, encoding="utf-8")


def test_default_is_warn_only_even_over_warning_thresholds() -> None:
    report = load_fresh("size_report_warn_only", Path(tempfile.mkdtemp()))
    # Tiny thresholds so a trivial fixture already exceeds them, without needing a
    # multi-megabyte file on disk just to exercise the warn-only exit path.
    report.WARN_RAW_BYTES = 10
    report.WARN_GZIP_BYTES = 10
    write_nodes_json(report.SITE_DATA_DIR / "nodes.json", 200)

    code, output = run_main(report, [])
    assert code == 0, output
    assert "⚠️" in output
    assert "FAIL" not in output


def test_fail_ceiling_below_actual_size_exits_nonzero() -> None:
    report = load_fresh("size_report_fail_below", Path(tempfile.mkdtemp()))
    write_nodes_json(report.SITE_DATA_DIR / "nodes.json", 2 * MIB)

    code, output = run_main(report, ["--fail-raw-mib", "1"])
    assert code == 1, output
    assert "FAIL: raw size" in output


def test_fail_ceiling_above_actual_size_exits_zero() -> None:
    report = load_fresh("size_report_fail_above", Path(tempfile.mkdtemp()))
    write_nodes_json(report.SITE_DATA_DIR / "nodes.json", 1 * MIB)

    code, output = run_main(report, ["--fail-raw-mib", "5"])
    assert code == 0, output
    assert "FAIL" not in output


def test_fail_ceiling_exact_equal_boundary_does_not_fail() -> None:
    # Both the fixture size and the ceiling are exact multiples of 1024*1024, so the
    # MiB -> byte conversion in main() is exact float arithmetic (multiplying/dividing
    # an exactly-representable integer by a power of two never rounds) — this isolates
    # the `>` vs `>=` comparison itself from floating-point boundary noise.
    report = load_fresh("size_report_fail_equal", Path(tempfile.mkdtemp()))
    write_nodes_json(report.SITE_DATA_DIR / "nodes.json", 1 * MIB)

    code, output = run_main(report, ["--fail-raw-mib", "1"])
    assert code == 0, output
    assert "FAIL" not in output


def test_invalid_ceiling_values_rejected() -> None:
    for bad_value in ["0", "-1", "nan", "inf", "not-a-number"]:
        report = load_fresh(f"size_report_invalid_{bad_value}", Path(tempfile.mkdtemp()))
        write_nodes_json(report.SITE_DATA_DIR / "nodes.json", 100)

        code, output = run_main(report, ["--fail-raw-mib", bad_value])
        assert code == 2, f"--fail-raw-mib {bad_value!r} -> exit {code}: {output}"

        code, output = run_main(report, ["--fail-gzip-mib", bad_value])
        assert code == 2, f"--fail-gzip-mib {bad_value!r} -> exit {code}: {output}"


def main() -> None:
    tests = [
        test_default_is_warn_only_even_over_warning_thresholds,
        test_fail_ceiling_below_actual_size_exits_nonzero,
        test_fail_ceiling_above_actual_size_exits_zero,
        test_fail_ceiling_exact_equal_boundary_does_not_fail,
        test_invalid_ceiling_values_rejected,
    ]
    for test in tests:
        test()
        print(f"  ok  {test.__name__}")
    print(f"\nAll {len(tests)} notes#29 size-report CLI checks passed.")


if __name__ == "__main__":
    main()
