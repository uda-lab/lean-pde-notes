#!/usr/bin/env python3
"""Regression checks for notes#7 corpus name collision handling."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def import_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_corpus(path: Path, name: str, statement: str, file: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [f"name: {name}"]
    if file is not None:
        fields.append(f"file: {file}")
    fields.extend([
        "tier: gloss",
        f"statement_ja: {statement}",
        "gap:",
        "  level: none",
        "chapter: misc",
    ])
    path.write_text("\n".join(fields) + "\n", encoding="utf-8")


def decl(id_: str, name: str, file: str, private: bool = False) -> dict:
    return {
        "id": id_,
        "name": name,
        "kind": "theorem",
        "private": private,
        "signature": "",
        "doc": "",
        "file": file,
        "startLine": 1,
        "endLine": 1,
        "deps": [],
    }


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


def patch_validate(module, root: Path) -> None:
    module.REPO_ROOT = root
    module.CORPUS_DIR = root / "corpus"
    module.EXTRACTED_DIR = root / "extracted"
    module.SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "corpus.schema.json"


def patch_build(module, root: Path) -> None:
    module.REPO_ROOT = root
    module.EXTRACTED_DIR = root / "extracted"
    module.CORPUS_DIR = root / "corpus"
    module.SITE_DATA_DIR = root / "site" / "data"
    module.CHAPTERS_PATH = root / "docs" / "schemas" / "chapters.yaml"


def test_validate_requires_file_for_collision() -> None:
    validate = import_script("validate_issue7_missing", REPO_ROOT / "scripts" / "validate.py")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        patch_validate(validate, root)
        write_json(root / "extracted" / "decls.json", [
            decl("LerayHopf.shared", "LerayHopf.shared", "A.lean"),
            decl("_private.B.shared", "LerayHopf.shared", "B.lean", private=True),
        ])
        (root / "extracted" / "PIN").write_text("a" * 40 + "\n", encoding="utf-8")
        write_corpus(root / "corpus" / "shared.yaml", "LerayHopf.shared", "共有補題。")

        code, output = run_main(validate, [])
        assert code == 1
        assert "file is required" in output
        assert "A.lean" in output and "B.lean" in output


def test_validate_accepts_collision_file_and_unique_name_without_file() -> None:
    validate = import_script("validate_issue7_success", REPO_ROOT / "scripts" / "validate.py")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        patch_validate(validate, root)
        write_json(root / "extracted" / "decls.json", [
            decl("LerayHopf.shared", "LerayHopf.shared", "A.lean"),
            decl("_private.B.shared", "LerayHopf.shared", "B.lean", private=True),
            decl("LerayHopf.unique", "LerayHopf.unique", "Unique.lean"),
        ])
        (root / "extracted" / "PIN").write_text("b" * 40 + "\n", encoding="utf-8")
        write_corpus(root / "corpus" / "shared_a.yaml", "LerayHopf.shared", "A側。", "A.lean")
        write_corpus(root / "corpus" / "shared_b.yaml", "LerayHopf.shared", "B側。", "B.lean")
        write_corpus(root / "corpus" / "unique.yaml", "LerayHopf.unique", "一意名。")

        code, output = run_main(validate, [])
        assert code == 0, output


def test_build_site_data_joins_collision_annotations_by_file_to_stable_id() -> None:
    build = import_script("build_issue7", REPO_ROOT / "scripts" / "build_site_data.py")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        patch_build(build, root)
        write_json(root / "extracted" / "decls.json", [
            decl("LerayHopf.shared", "LerayHopf.shared", "A.lean"),
            decl("_private.B.shared", "LerayHopf.shared", "B.lean", private=True),
            decl("LerayHopf.unique", "LerayHopf.unique", "Unique.lean"),
        ])
        (root / "extracted" / "PIN").write_text("c" * 40 + "\n", encoding="utf-8")
        write_corpus(root / "corpus" / "shared_a.yaml", "LerayHopf.shared", "A側。", "A.lean")
        write_corpus(root / "corpus" / "shared_b.yaml", "LerayHopf.shared", "B側。", "B.lean")
        write_corpus(root / "corpus" / "unique.yaml", "LerayHopf.unique", "一意名。")

        out_path = root / "nodes.json"
        code, output = run_main(build, ["--out", str(out_path), "--no-coverage"])
        assert code == 0, output
        assert "Collision groups: 1" in output

        payload = json.loads(out_path.read_text(encoding="utf-8"))
        by_id = {node["id"]: node for node in payload["nodes"]}
        assert by_id["LerayHopf.shared"]["slug"] == "LerayHopf.shared"
        assert by_id["LerayHopf.shared"]["corpus"]["statement_ja"] == "A側。"
        assert by_id["_private.B.shared"]["slug"] == "_private.B.shared"
        assert by_id["_private.B.shared"]["corpus"]["statement_ja"] == "B側。"
        assert by_id["LerayHopf.unique"]["slug"] == "LerayHopf.unique"
        assert by_id["LerayHopf.unique"]["corpus"]["statement_ja"] == "一意名。"


def main() -> None:
    tests = [
        test_validate_requires_file_for_collision,
        test_validate_accepts_collision_file_and_unique_name_without_file,
        test_build_site_data_joins_collision_annotations_by_file_to_stable_id,
    ]
    for test in tests:
        test()
        print(f"  ok  {test.__name__}")
    print(f"\nAll {len(tests)} issue #7 disambiguation checks passed.")


if __name__ == "__main__":
    main()
