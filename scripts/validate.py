#!/usr/bin/env python3
"""
validate.py — corpus integrity checker for leray-hopf-notes.

Checks:
  1. Every corpus/**/*.yaml parses as valid YAML.
  2. Every corpus YAML conforms to docs/schemas/corpus.schema.json (JSON Schema draft-07).
  3. The corpus name-set is a subset of the extracted name-set
     (prefers extracted/decls.json, falls back to extracted/names-fallback.json).
     When decls.json has duplicate display names, matching corpus entries must
     include `file` and the pair (name, file) must identify one extracted record.
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

sys.path.insert(0, str(Path(__file__).parent))
from bibliography import ID_PATTERN, parse_bibliography  # noqa: E402

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
VALID_PROOF_STATUSES = {'verified', 'contains-sorry', 'scaffold', 'retired', 'invalid-statement'}
VALID_CHAPTERS = {
    'spaces', 'projections-galerkin', 'ode', 'energy', 'compactness',
    'limit-passage', 'capstone-r3', 'capstone-torus', 'bochner',
    'galerkin-generic', 'misc',
}
NAME_PATTERN = re.compile(r"^[A-Za-z_Ͱ-￿][A-Za-z0-9_'.Ͱ-￿]*$")


def load_schema() -> dict | None:
    if not SCHEMA_PATH.exists():
        return None
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_name_universe() -> tuple[set[str], set[tuple[str, str]], dict[str, set[str]], str]:
    """Return (name_set, keyed_set, collision_files_by_name, source_label)."""
    decls_path = EXTRACTED_DIR / 'decls.json'
    fallback_path = EXTRACTED_DIR / 'names-fallback.json'
    if decls_path.exists():
        with open(decls_path, encoding='utf-8') as f:
            data = json.load(f)
        names = {d['name'] for d in data}
        keyed = {(d['name'], d.get('file', '')) for d in data}
        counts: dict[str, int] = {}
        for d in data:
            counts[d['name']] = counts.get(d['name'], 0) + 1
        collision_names = {name for name, count in counts.items() if count > 1}
        collisions = {
            name: {d.get('file', '') for d in data if d['name'] == name}
            for name in collision_names
        }
        return names, keyed, collisions, 'extracted/decls.json'
    if fallback_path.exists():
        with open(fallback_path, encoding='utf-8') as f:
            data = json.load(f)
        names = {d['name'] for d in data}
        keyed = {(d['name'], d.get('file', '')) for d in data}
        return names, keyed, {}, 'extracted/names-fallback.json'
    return set(), set(), {}, '(no universe — skipping name check)'


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

    proof_status = doc.get('proof_status')
    if proof_status is not None and proof_status not in VALID_PROOF_STATUSES:
        errs.append(
            f'{fpath}: proof_status "{proof_status}" must be one of {sorted(VALID_PROOF_STATUSES)}'
        )

    references = doc.get('references')
    if references is not None:
        if not isinstance(references, list) or not references:
            errs.append(f'{fpath}: references must be a non-empty array')
        else:
            for ref in references:
                if not isinstance(ref, dict) or not isinstance(ref.get('id'), str):
                    errs.append(f'{fpath}: each references[] entry must be an object with a string "id"')
                elif not ID_PATTERN.match(ref['id']):
                    errs.append(f'{fpath}: references[].id "{ref["id"]}" must match ^[a-z][a-z0-9-]*$')

    return errs


def check_references(doc: dict, fpath: Path, bib_ids: set[str]) -> list[str]:
    """Cross-check `references[].id` against docs/bibliography.md entries.

    Runs regardless of jsonschema availability: the JSON Schema only checks the
    `references[].id` shape (lowercase-hyphen pattern), not that the id actually
    resolves to a known bibliography entry — that requires reading bibliography.md.
    """
    errs: list[str] = []
    refs = doc.get('references')
    if not refs:
        return errs
    if not isinstance(refs, list):
        return errs  # schema check (or validate_schema_manual, if extended) covers shape
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        rid = ref.get('id')
        if rid and rid not in bib_ids:
            errs.append(
                f'{fpath}: references[].id "{rid}" not found in docs/bibliography.md '
                f'(known ids: {", ".join(sorted(bib_ids)) or "(none parsed)"})'
            )
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

    bibliography = parse_bibliography()
    bib_ids = set(bibliography.keys())
    if not bib_ids:
        # Do NOT skip check_references below: an empty bib_ids set still lets every
        # corpus references[].id fail to resolve (correctly, via check_references'
        # "not in bib_ids" test) rather than silently passing CI while the bibliography
        # itself is broken or missing — a docs/bibliography.md deletion or heading-format
        # regression must not go unnoticed just because it happens to make the id-lookup
        # trivially permissive.
        warnings.append(
            'WARNING: docs/bibliography.md parsed 0 citation ids — any corpus '
            'references[] entry will now fail its id-resolution check'
        )

    universe, keyed_universe, collisions, universe_source = load_name_universe()
    print(f'Name universe: {len(universe)} names from {universe_source}')

    # Check PIN when decls.json is present
    decls_path = EXTRACTED_DIR / 'decls.json'
    pin = None
    if decls_path.exists():
        pin_path = EXTRACTED_DIR / 'PIN'
        if not pin_path.exists():
            errors.append('ERROR: extracted/decls.json present but extracted/PIN missing')
        else:
            pin = pin_path.read_text(encoding='utf-8').strip()
            if not re.fullmatch(r'[0-9a-fA-F]{40}', pin):
                errors.append(f'ERROR: extracted/PIN is not a 40-char hex SHA: "{pin}"')

    # notes#68: CITATION.cff's references[0].commit is a manually-maintained pin of the
    # companion leray-hopf repo (see the inline comment in CITATION.cff). A repin PR that
    # updates extracted/PIN but forgets CITATION.cff silently drifts the citation out of
    # sync with the actual source — this happened once already (caught during notes#68
    # development, days after notes#66 landed the field). Hard-fail so it can't recur.
    citation_path = REPO_ROOT / 'CITATION.cff'
    if pin and citation_path.exists():
        with open(citation_path, encoding='utf-8') as f:
            cff = yaml.safe_load(f)
        refs = cff.get('references') if isinstance(cff, dict) else None
        source = refs[0] if isinstance(refs, list) and refs and isinstance(refs[0], dict) else None
        cff_commit = source.get('commit') if source else None
        if cff_commit and cff_commit != pin:
            errors.append(
                f'ERROR: CITATION.cff references[0].commit ("{cff_commit}") does not match '
                f'extracted/PIN ("{pin}") — update CITATION.cff to match the current repin'
            )
        elif not cff_commit:
            warnings.append(
                'WARNING: CITATION.cff has no references[0].commit to cross-check against '
                'extracted/PIN (unexpected shape, or the field was removed) — the pin-drift '
                'check notes#68 added could not run'
            )

    corpus_names: set[str] = set()
    corpus_keys: set[tuple[str, str]] = set()
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

        errors.extend(check_references(doc, fpath, bib_ids))

        # notes#65 safety net: proof_status defaults to 'verified' when absent, so a corpus
        # entry whose own prose admits an intentionally-open `sorry` but never sets
        # proof_status would silently render as an ordinary proved theorem. Catch that drift
        # here. Matched narrowly against the "意図的...sorry" / "ALLOW_SORRY" phrasing this
        # corpus already uses for a genuine open sorry on the declaration itself — a bare
        # "sorry" substring match is too broad: many proved entries say "sorry なし" (no
        # sorry) about themselves, or mention that a *dependency* still has one.
        proof_status = doc.get('proof_status') or 'verified'
        if proof_status == 'verified':
            prose = ' '.join(str(doc.get(f, '') or '') for f in ('statement_ja', 'proof_ja'))
            gap_note = str((doc.get('gap') or {}).get('note', '') or '')
            haystack = prose + ' ' + gap_note
            if 'ALLOW_SORRY' in haystack or re.search(r'意図的.{0,20}sorry|sorry.{0,20}意図的', haystack):
                warnings.append(
                    f'WARNING: {fpath}: prose reads as an intentionally-open sorry '
                    f'("意図的"/ALLOW_SORRY) but proof_status is absent/verified — set '
                    f'proof_status: contains-sorry (or another non-verified status) if this '
                    f'declaration itself has an open sorry'
                )

        # Collect name for universe check
        name = doc.get('name')
        if name:
            corpus_names.add(name)
            file = doc.get('file')
            if name in collisions:
                if not isinstance(file, str) or not file.strip():
                    choices = ', '.join(sorted(collisions[name]))
                    errors.append(
                        f'ERROR: {fpath}: file is required because "{name}" is ambiguous in '
                        f'{universe_source}; expected one of: {choices}'
                    )
                elif (name, file) not in keyed_universe:
                    choices = ', '.join(sorted(collisions[name]))
                    errors.append(
                        f'ERROR: {fpath}: (name, file)=("{name}", "{file}") not found in '
                        f'{universe_source}; expected file one of: {choices}'
                    )
            key = (name, file) if name in collisions else (name, '')
            if key in corpus_keys:
                if name in collisions:
                    errors.append(
                        f'ERROR: duplicate corpus annotation for (name, file)=("{name}", "{file}")'
                    )
                else:
                    errors.append(f'ERROR: duplicate corpus annotation for name "{name}"')
            corpus_keys.add(key)

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
