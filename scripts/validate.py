#!/usr/bin/env python3
"""
validate.py — corpus integrity checker for lean-pde-notes.

Checks:
  1. Every corpus/**/*.yaml parses as valid YAML.
  2. Every corpus YAML conforms to docs/schemas/corpus.schema.json (JSON Schema draft-07).
  3. The corpus name-set is a subset of the extracted name-set
     (prefers extracted/decls.json, falls back to extracted/names-fallback.json).
  4. When decls.json is present, extracted/PIN exists and is a 40-char hex SHA.

Usage:
    python3 scripts/validate.py              # from repo root
    python3 scripts/validate.py --strict     # exit 1 on any warning too
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    sys.exit('ERROR: PyYAML is required. Install with: pip install pyyaml')

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


REPO_ROOT = Path(__file__).parent.parent
CORPUS_DIR = REPO_ROOT / 'corpus'
EXTRACTED_DIR = REPO_ROOT / 'extracted'
SCHEMA_PATH = REPO_ROOT / 'docs' / 'schemas' / 'corpus.schema.json'

VALID_TIERS = {'full', 'gloss'}
VALID_GAP_LEVELS = {'none', 'mild', 'large'}
VALID_CHAPTERS = {
    'spaces', 'projections-galerkin', 'ode', 'energy', 'compactness',
    'limit-passage', 'capstone-r3', 'capstone-torus', 'bochner', 'misc',
}
NAME_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$')


def load_schema() -> dict | None:
    if not SCHEMA_PATH.exists():
        return None
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_name_universe() -> tuple[set[str], str]:
    """Return (name_set, source_label)."""
    decls_path = EXTRACTED_DIR / 'decls.json'
    fallback_path = EXTRACTED_DIR / 'names-fallback.json'
    if decls_path.exists():
        with open(decls_path, encoding='utf-8') as f:
            data = json.load(f)
        names = {d['name'] for d in data}
        return names, 'extracted/decls.json'
    if fallback_path.exists():
        with open(fallback_path, encoding='utf-8') as f:
            data = json.load(f)
        names = {d['name'] for d in data}
        return names, 'extracted/names-fallback.json'
    return set(), '(no universe — skipping name check)'


def validate_schema_manual(doc: dict, fpath: Path) -> list[str]:
    """Lightweight manual schema check used when jsonschema is unavailable."""
    errs: list[str] = []

    required = ['name', 'tier', 'statement_ja', 'gap', 'chapter']
    for field in required:
        if field not in doc:
            errs.append(f'{fpath}: missing required field "{field}"')

    name = doc.get('name', '')
    if name and not NAME_PATTERN.match(name):
        errs.append(f'{fpath}: name "{name}" does not match fully-qualified Lean name pattern')

    tier = doc.get('tier')
    if tier and tier not in VALID_TIERS:
        errs.append(f'{fpath}: tier "{tier}" must be one of {sorted(VALID_TIERS)}')

    stmt = doc.get('statement_ja', '')
    if stmt is not None and len(str(stmt).strip()) == 0:
        errs.append(f'{fpath}: statement_ja is empty')

    gap = doc.get('gap')
    if gap is not None:
        if not isinstance(gap, dict):
            errs.append(f'{fpath}: gap must be an object')
        else:
            level = gap.get('level')
            if level not in VALID_GAP_LEVELS:
                errs.append(f'{fpath}: gap.level "{level}" must be one of {sorted(VALID_GAP_LEVELS)}')
            if level == 'large' and not gap.get('note', '').strip():
                errs.append(f'{fpath}: gap.note is required when gap.level=large')

    chapter = doc.get('chapter')
    if chapter and chapter not in VALID_CHAPTERS:
        errs.append(f'{fpath}: chapter "{chapter}" not in known chapters {sorted(VALID_CHAPTERS)}')

    return errs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true',
                        help='Exit 1 on warnings as well as errors')
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    schema = load_schema()
    if schema is None:
        warnings.append(f'WARNING: Schema file not found at {SCHEMA_PATH} — structural checks skipped')

    universe, universe_source = load_name_universe()
    print(f'Name universe: {len(universe)} names from {universe_source}')

    # Check PIN when decls.json is present
    decls_path = EXTRACTED_DIR / 'decls.json'
    if decls_path.exists():
        pin_path = EXTRACTED_DIR / 'PIN'
        if not pin_path.exists():
            errors.append('ERROR: extracted/decls.json present but extracted/PIN missing')
        else:
            pin = pin_path.read_text(encoding='utf-8').strip()
            if not re.fullmatch(r'[0-9a-fA-F]{40}', pin):
                errors.append(f'ERROR: extracted/PIN is not a 40-char hex SHA: "{pin}"')

    corpus_names: set[str] = set()
    yaml_files = sorted(CORPUS_DIR.rglob('*.yaml'))
    print(f'Corpus files: {len(yaml_files)}')

    for fpath in yaml_files:
        # Skip README and schema files
        if fpath.name in ('README.yaml',):
            continue

        try:
            with open(fpath, encoding='utf-8') as f:
                doc = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            errors.append(f'ERROR: {fpath}: YAML parse error: {exc}')
            continue

        if not isinstance(doc, dict):
            errors.append(f'ERROR: {fpath}: top-level value must be a mapping')
            continue

        # Schema validation
        if HAS_JSONSCHEMA and schema is not None:
            try:
                jsonschema.validate(doc, schema)
            except jsonschema.ValidationError as exc:
                errors.append(f'ERROR: {fpath}: schema violation: {exc.message}')
        else:
            errs = validate_schema_manual(doc, fpath)
            errors.extend(errs)

        # Collect name for universe check
        name = doc.get('name')
        if name:
            corpus_names.add(name)

    # Check corpus ⊆ universe
    if universe:
        extra = corpus_names - universe
        if extra:
            for name in sorted(extra):
                errors.append(
                    f'ERROR: corpus name "{name}" not found in {universe_source}'
                )
    else:
        if corpus_names:
            warnings.append(
                f'WARNING: no name universe available — cannot check corpus names against extracted'
            )

    # Summary
    if errors:
        print(f'\n{len(errors)} error(s) found:')
        for e in errors:
            print(f'  {e}')
    if warnings:
        print(f'\n{len(warnings)} warning(s):')
        for w in warnings:
            print(f'  {w}')

    if not errors and not warnings:
        print(f'OK — {len(yaml_files)} corpus files valid, all names in universe.')
    elif not errors:
        print(f'\nOK (with warnings) — {len(yaml_files)} corpus files valid.')

    if errors:
        sys.exit(1)
    if args.strict and warnings:
        sys.exit(1)


if __name__ == '__main__':
    main()
