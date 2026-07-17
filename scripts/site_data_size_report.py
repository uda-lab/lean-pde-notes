#!/usr/bin/env python3
"""
site_data_size_report.py — compute raw and gzip sizes for generated site data

Produces a markdown summary suitable for CI logs and optionally writes
a machine-readable JSON report.

Usage:
    python3 scripts/site_data_size_report.py [--json output.json]
        [--fail-raw-mib MIB] [--fail-gzip-mib MIB]
"""

import json
import gzip
import math
import sys
from pathlib import Path
from typing import Dict, Optional
import argparse

# Module-level so tests (and any future caller) can monkeypatch these instead of
# reaching into a hardcoded relative path / literal buried inside main().
SITE_DATA_DIR = Path("site/data")

# Warning thresholds (visibility only — these never fail the script; see
# --fail-raw-mib/--fail-gzip-mib below for the opt-in hard ceiling).
WARN_RAW_BYTES = 10 * 1024 * 1024
WARN_GZIP_BYTES = 3 * 1024 * 1024


def get_file_sizes(path: Path) -> Dict[str, int]:
    """Return raw and gzip sizes for a file."""
    if not path.exists():
        return {"raw": 0, "gzip": 0}

    raw_size = path.stat().st_size

    # Compute gzip size
    with open(path, "rb") as f:
        data = f.read()
    gzip_size = len(gzip.compress(data, compresslevel=6))

    return {"raw": raw_size, "gzip": gzip_size}


def format_bytes(size: int) -> str:
    """Format bytes as a human-readable binary (1024-based) string, e.g. '3.2 MiB'."""
    for unit in ["B", "KiB", "MiB", "GiB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TiB"


def positive_finite_mib(value: str) -> float:
    """argparse type= for --fail-raw-mib/--fail-gzip-mib: reject non-numeric, non-finite
    (NaN/inf — NaN in particular would silently disable the ceiling, since every
    comparison against NaN is false), and non-positive (<=0 would always "breach")."""
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not a valid number") from exc
    if not math.isfinite(parsed):
        raise argparse.ArgumentTypeError(f"{value!r} must be finite, got {parsed}")
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"{value!r} must be strictly positive")
    return parsed


def estimate_bucket_sizes(nodes_path: Path, sources_path: Path) -> Dict[str, Dict[str, int]]:
    """
    Estimate size breakdown by data category.
    
    Returns approximate raw byte counts for:
    - structural: id, name, kind, private, file, line range, flags, chapter
    - signature_doc: signature, doc fields
    - graph: uses, usedBy arrays
    - corpus: corpus object (statement_ja, proof_ja, gap, tags, tier)
    - source: source bodies in sources.json
    """
    buckets = {
        "structural": {"raw": 0},
        "signature_doc": {"raw": 0},
        "graph": {"raw": 0},
        "corpus": {"raw": 0},
        "source": {"raw": 0},
    }
    
    if not nodes_path.exists():
        return buckets
    
    with open(nodes_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # nodes.json has structure: {"nodes": [...], ...}
    nodes = data.get("nodes", [])
    
    # Estimate per-field sizes (simplified heuristic)
    for node in nodes:
        # Structural metadata
        structural_keys = ["id", "name", "kind", "private", "file", "startLine", 
                          "endLine", "chapter", "slug", "shortName", "capstone", 
                          "collision", "has_source"]
        for key in structural_keys:
            if key in node:
                buckets["structural"]["raw"] += len(json.dumps(node[key], ensure_ascii=False))
        
        # Signature and doc
        sig_doc_keys = ["signature", "doc"]
        for key in sig_doc_keys:
            if key in node:
                buckets["signature_doc"]["raw"] += len(json.dumps(node[key], ensure_ascii=False))
        
        # Graph edges
        graph_keys = ["uses", "usedBy"]
        for key in graph_keys:
            if key in node:
                buckets["graph"]["raw"] += len(json.dumps(node[key], ensure_ascii=False))
        
        # Corpus annotations (stored as a nested object)
        if "corpus" in node and node["corpus"]:
            buckets["corpus"]["raw"] += len(json.dumps(node["corpus"], ensure_ascii=False))
    
    # Source bodies
    if sources_path.exists():
        with open(sources_path, "r", encoding="utf-8") as f:
            sources_data = json.load(f)
        # sources.json structure: {"pin": "...", "source_count": N, "sources": {slug: text, ...}}
        source_map = sources_data.get("sources", {})
        buckets["source"]["raw"] = sum(len(json.dumps(src, ensure_ascii=False)) for src in source_map.values())
    
    return buckets


def project_growth(current_decls: int, current_raw: int, current_gzip: int, 
                  additional: int) -> Dict[str, int]:
    """Project sizes with additional declarations using current slope."""
    if current_decls == 0:
        return {"raw": 0, "gzip": 0}
    
    raw_per_decl = current_raw / current_decls
    gzip_per_decl = current_gzip / current_decls
    
    projected_decls = current_decls + additional
    return {
        "raw": int(raw_per_decl * projected_decls),
        "gzip": int(gzip_per_decl * projected_decls),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate size report for site data")
    parser.add_argument("--json", metavar="PATH", help="Write machine-readable JSON report")
    parser.add_argument(
        "--fail-raw-mib", type=positive_finite_mib, default=None, metavar="MIB",
        help="Exit non-zero if combined raw size exceeds this many MiB (hard ceiling; "
             "unset means never fail, matching the warn-only default). Must be a finite, "
             "strictly positive number.",
    )
    parser.add_argument(
        "--fail-gzip-mib", type=positive_finite_mib, default=None, metavar="MIB",
        help="Exit non-zero if combined gzip size exceeds this many MiB (hard ceiling; "
             "unset means never fail, matching the warn-only default). Must be a finite, "
             "strictly positive number.",
    )
    args = parser.parse_args()

    # Paths to generated files
    nodes_path = SITE_DATA_DIR / "nodes.json"
    sources_path = SITE_DATA_DIR / "sources.json"
    coverage_path = SITE_DATA_DIR / "coverage.json"
    
    # Compute sizes
    nodes_sizes = get_file_sizes(nodes_path)
    sources_sizes = get_file_sizes(sources_path)
    coverage_sizes = get_file_sizes(coverage_path)
    
    total_raw = nodes_sizes["raw"] + sources_sizes["raw"] + coverage_sizes["raw"]
    total_gzip = nodes_sizes["gzip"] + sources_sizes["gzip"] + coverage_sizes["gzip"]
    
    # Count declarations
    decl_count = 0
    if nodes_path.exists():
        with open(nodes_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            nodes = data.get("nodes", [])
            decl_count = len(nodes)
    
    # Bucket estimates
    buckets = estimate_bucket_sizes(nodes_path, sources_path)
    
    # Growth projections
    projections = {
        "+100": project_growth(decl_count, total_raw, total_gzip, 100),
        "+500": project_growth(decl_count, total_raw, total_gzip, 500),
        "+1000": project_growth(decl_count, total_raw, total_gzip, 1000),
    }
    
    # Build report
    report = {
        "declaration_count": decl_count,
        "files": {
            "nodes.json": nodes_sizes,
            "sources.json": sources_sizes,
            "coverage.json": coverage_sizes,
        },
        "total": {
            "raw": total_raw,
            "gzip": total_gzip,
        },
        "slopes": {
            "raw_per_decl": total_raw / decl_count if decl_count > 0 else 0,
            "gzip_per_decl": total_gzip / decl_count if decl_count > 0 else 0,
        },
        "buckets": buckets,
        "projections": projections,
    }
    
    # Write JSON report if requested
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"JSON report written to {args.json}", file=sys.stderr)
    
    # Print markdown summary
    print("# Site Data Size Report\n")
    print(f"**Declaration count:** {decl_count}\n")
    
    # Detect build mode
    source_count = 0
    if sources_path.exists():
        with open(sources_path, "r", encoding="utf-8") as f:
            sources_data = json.load(f)
            source_count = sources_data.get("source_count", 0)
    
    build_mode = "source-enabled" if source_count > 0 else "source-less"
    print(f"**Build mode:** {build_mode} ({source_count} declarations with embedded source)\n")
    
    print("## Current Sizes\n")
    print("| File | Raw | Gzip |")
    print("|------|-----|------|")
    print(f"| nodes.json | {format_bytes(nodes_sizes['raw'])} | {format_bytes(nodes_sizes['gzip'])} |")
    print(f"| sources.json | {format_bytes(sources_sizes['raw'])} | {format_bytes(sources_sizes['gzip'])} |")
    print(f"| coverage.json | {format_bytes(coverage_sizes['raw'])} | {format_bytes(coverage_sizes['gzip'])} |")
    print(f"| **Total** | **{format_bytes(total_raw)}** | **{format_bytes(total_gzip)}** |")
    print()
    
    print("## Per-Declaration Slopes\n")
    if decl_count > 0:
        print(f"- Raw: {report['slopes']['raw_per_decl']:.1f} bytes/decl")
        print(f"- Gzip: {report['slopes']['gzip_per_decl']:.1f} bytes/decl")
    else:
        print("(No declarations found)")
    print()
    
    print("## Bucket Estimates\n")
    print("| Category | Raw Size |")
    print("|----------|----------|")
    for bucket_name, bucket_data in buckets.items():
        print(f"| {bucket_name} | {format_bytes(bucket_data['raw'])} |")
    print()
    
    print("## Growth Projections\n")
    print("| Additional Decls | Total Raw | Total Gzip |")
    print("|------------------|-----------|------------|")
    for label, proj in projections.items():
        print(f"| {label} | {format_bytes(proj['raw'])} | {format_bytes(proj['gzip'])} |")
    print()
    
    # Threshold checks
    print("## Budget Status\n")

    raw_warning = WARN_RAW_BYTES
    gzip_warning = WARN_GZIP_BYTES

    warnings = []
    if total_raw > raw_warning:
        warnings.append(f"⚠️  Raw size {format_bytes(total_raw)} exceeds {format_bytes(raw_warning)} warning threshold")
    if total_gzip > gzip_warning:
        warnings.append(f"⚠️  Gzip size {format_bytes(total_gzip)} exceeds {format_bytes(gzip_warning)} warning threshold")
    
    if warnings:
        for warning in warnings:
            print(warning)
        print()
    else:
        print(f"✓ Within budget (raw < {format_bytes(raw_warning)}, gzip < {format_bytes(gzip_warning)})")
        print()

    # Hard failure ceiling: opt-in via --fail-raw-mib/--fail-gzip-mib, unset by default so
    # the report stays warn-only unless a caller (e.g. CI) explicitly wires a ceiling.
    failures = []
    if args.fail_raw_mib is not None:
        raw_ceiling = args.fail_raw_mib * 1024 * 1024
        if total_raw > raw_ceiling:
            failures.append(
                f"FAIL: raw size {format_bytes(total_raw)} exceeds hard ceiling {args.fail_raw_mib:g} MiB"
            )
    if args.fail_gzip_mib is not None:
        gzip_ceiling = args.fail_gzip_mib * 1024 * 1024
        if total_gzip > gzip_ceiling:
            failures.append(
                f"FAIL: gzip size {format_bytes(total_gzip)} exceeds hard ceiling {args.fail_gzip_mib:g} MiB"
            )

    if failures:
        for failure in failures:
            print(failure)
        print()
        sys.exit(1)

    # Exit 0 even when over the warn-only threshold above (visibility, not blocking).
    if warnings:
        sys.exit(0)


if __name__ == "__main__":
    main()
