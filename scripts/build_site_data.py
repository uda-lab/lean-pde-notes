#!/usr/bin/env python3
"""
build_site_data.py — join extracted declaration metadata with the annotation corpus
into a single static JSON payload for the site/ viewer.

Inputs
  extracted/decls.json          (preferred) full metadata: id, name, kind, private,
                                signature, doc, file, startLine, endLine, deps[id-refs]
  extracted/names-fallback.json (fallback)  name, kind, file, line   — skeleton only
  extracted/PIN                 40-char lean-pde SHA (recorded into the output)
  corpus/**/*.yaml              per-declaration annotations (joined by display name)
  docs/schemas/chapters.yaml    chapter taxonomy (ids + Japanese labels)

Output
  site/data/nodes.json          one deterministic payload the SPA loads in full.
  site/data/coverage.json       refreshed by shelling out to scripts/coverage.py.

Join model
  * `deps` edges reference declaration **ids** (unique). Nodes are keyed by a URL
    **slug**: the display `name` when that name is unique in the universe, else the
    (always-unique) `id`. This keeps slugs readable for the common case while staying
    unambiguous for the private-helper name collisions.
  * The corpus is keyed by display `name`. When a name is unique we attach its YAML.
    When a name belongs to a collision group (see notes#7) the join is ambiguous, so
    those records are emitted WITHOUT corpus data and listed in a warning. The corpus
    schema has no `file` tiebreaker yet; adding it is deferred to notes#7.

Determinism: nodes are sorted by slug, edge lists are sorted, and json.dump uses
sort_keys=True so the committed output diffs cleanly.

Usage:
    python3 scripts/build_site_data.py
    python3 scripts/build_site_data.py --no-coverage   # skip coverage.py refresh
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit('ERROR: PyYAML required. pip install pyyaml')

REPO_ROOT = Path(__file__).parent.parent
EXTRACTED_DIR = REPO_ROOT / 'extracted'
CORPUS_DIR = REPO_ROOT / 'corpus'
SITE_DATA_DIR = REPO_ROOT / 'site' / 'data'
CHAPTERS_PATH = REPO_ROOT / 'docs' / 'schemas' / 'chapters.yaml'

# ---------------------------------------------------------------------------
# Chapter heuristic (fallback only — a corpus `chapter:` field always wins).
#
# Ordered (module-path substring -> chapter id); first match wins. The order
# encodes precedence where a path matches several substrings, e.g. a capstone
# file also contains "GalerkinODE", and "TorusEnergyConvection" contains both
# "Energy" and "Convection" (Energy wins, intentionally). Anything unmatched
# falls to `misc`. This is deliberately coarse: precise per-decl classification
# is a corpus/annotation job, not a filename job.
# ---------------------------------------------------------------------------
CHAPTER_RULES = [
    ('/Bochner/', 'bochner'),
    ('R3/GalerkinODECapstone', 'capstone-r3'),
    ('R3/AxiomaticClosure', 'capstone-r3'),
    ('TorusGalerkinODECapstone', 'capstone-torus'),
    ('LerayHopf/AxiomaticClosure.lean', 'capstone-torus'),
    ('LimitPassage', 'limit-passage'),
    ('Rellich', 'compactness'),
    ('FrechetKolmogorov', 'compactness'),
    ('ArzelaAscoli', 'compactness'),
    ('SpatialCompactness', 'compactness'),
    ('SpacetimePrecompact', 'compactness'),
    ('SobolevEmbedding', 'compactness'),
    ('AubinLions', 'compactness'),
    ('ModeCompactness', 'compactness'),
    ('ModeTail', 'compactness'),
    ('GalerkinODE', 'ode'),
    ('GalerkinCurveBounds', 'ode'),
    ('GalerkinTimeModulus', 'ode'),
    ('Energy', 'energy'),
    ('ViscousLimit', 'energy'),
    ('GalerkinProjection', 'projections-galerkin'),
    ('GalerkinScheme', 'projections-galerkin'),
    ('GalerkinBasis', 'projections-galerkin'),
    ('SchwartzDivFreeBasis', 'projections-galerkin'),
    ('VelocityGalerkin', 'projections-galerkin'),
    ('ProjectionAdjoint', 'projections-galerkin'),
    ('GalerkinPackage', 'projections-galerkin'),
    ('LerayHopf/Leray.lean', 'projections-galerkin'),
    ('Convection', 'limit-passage'),
    ('Trilinear', 'limit-passage'),
    ('CurlDensity', 'limit-passage'),
    ('WeightedFourierCommute', 'limit-passage'),
    ('TensorIntersection', 'limit-passage'),
    ('FunctionSpaces', 'spaces'),
    ('H1Sigma', 'spaces'),
    ('DivergenceFree', 'spaces'),
    ('EvolutionTriple', 'spaces'),
    ('FourierL2', 'spaces'),
    ('SobolevTorus', 'spaces'),
    ('Domain', 'spaces'),
    ('Regularity', 'spaces'),
    ('TestFamily', 'spaces'),
    ('Basic', 'spaces'),
]

CAPSTONE_NAMES = {
    'LerayHopf.exists_lerayHopf_r3_axiomatic',
    'LerayHopf.exists_lerayHopf_torus3_axiomatic',
}


def chapter_for_file(file_path: str) -> str:
    for needle, chapter in CHAPTER_RULES:
        if needle in file_path:
            return chapter
    return 'misc'


def load_universe():
    """Return (records, source_label, has_decls). Records are normalized dicts."""
    decls_path = EXTRACTED_DIR / 'decls.json'
    fallback_path = EXTRACTED_DIR / 'names-fallback.json'
    if decls_path.exists():
        with open(decls_path, encoding='utf-8') as f:
            return json.load(f), 'extracted/decls.json', True
    if fallback_path.exists():
        with open(fallback_path, encoding='utf-8') as f:
            data = json.load(f)
        # Normalize fallback shape (name, kind, file, line) to the decls shape.
        norm = []
        for r in data:
            norm.append({
                'id': r['name'],
                'name': r['name'],
                'kind': r.get('kind', 'other'),
                'private': r.get('private', False),
                'signature': r.get('signature', ''),
                'doc': r.get('doc', ''),
                'file': r.get('file', ''),
                'startLine': r.get('line', 0),
                'endLine': r.get('line', 0),
                'deps': [],
            })
        return norm, 'extracted/names-fallback.json', False
    return [], '(none)', False


def load_chapters():
    if not CHAPTERS_PATH.exists():
        return []
    with open(CHAPTERS_PATH, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('chapters', []) if isinstance(data, dict) else []


def load_corpus():
    """Return {name: [(path, doc), ...]} keyed by display name."""
    by_name = defaultdict(list)
    for fpath in sorted(CORPUS_DIR.rglob('*.yaml')):
        try:
            with open(fpath, encoding='utf-8') as f:
                doc = yaml.safe_load(f)
        except (yaml.YAMLError, OSError):
            continue
        if isinstance(doc, dict) and doc.get('name'):
            by_name[doc['name']].append((fpath, doc))
    return by_name


def corpus_payload(doc: dict) -> dict:
    """Project a corpus YAML into the site-facing shape (sample flag derived from tags)."""
    tags = doc.get('tags') or []
    payload = {
        'tier': doc.get('tier'),
        'statement_ja': doc.get('statement_ja', ''),
        'gap': doc.get('gap') or {'level': 'none'},
        'chapter': doc.get('chapter'),
        'tags': tags,
        'sample': 'sample' in tags,
    }
    if doc.get('proof_ja'):
        payload['proof_ja'] = doc['proof_ja']
    return payload


def read_pin() -> str:
    pin_path = EXTRACTED_DIR / 'PIN'
    if pin_path.exists():
        return pin_path.read_text(encoding='utf-8').strip()
    return ''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-coverage', action='store_true',
                        help='Do not shell out to coverage.py')
    args = parser.parse_args()

    records, source, has_decls = load_universe()
    if not records:
        sys.exit('ERROR: no name universe (extracted/decls.json or names-fallback.json).')
    print(f'Universe: {len(records)} records from {source}')

    chapters = load_chapters()
    corpus_by_name = load_corpus()

    # Name -> record(s); a name is a collision when it maps to >1 record.
    name_to_records = defaultdict(list)
    for r in records:
        name_to_records[r['name']].append(r)
    collisions = {n: rs for n, rs in name_to_records.items() if len(rs) > 1}

    # id -> slug (deps reference ids); slug = name if unique else id.
    def slug_of(rec):
        return rec['name'] if len(name_to_records[rec['name']]) == 1 else rec['id']

    id_to_slug = {r['id']: slug_of(r) for r in records}

    warnings: list[str] = []

    # Warn on any corpus entry that targets a collision name (join deferred to notes#7).
    for name, entries in sorted(corpus_by_name.items()):
        if name in collisions:
            for fpath, _ in entries:
                warnings.append(
                    f'corpus {fpath.relative_to(REPO_ROOT)} targets collision name '
                    f'"{name}" ({len(collisions[name])} decls) — join DEFERRED to notes#7'
                )

    # Build nodes.
    nodes_by_slug: dict[str, dict] = {}
    for r in records:
        slug = slug_of(r)
        is_collision = r['name'] in collisions

        corpus = None
        if not is_collision:
            entries = corpus_by_name.get(r['name'])
            if entries:
                if len(entries) > 1:
                    files = ', '.join(str(p.relative_to(REPO_ROOT)) for p, _ in entries)
                    warnings.append(
                        f'name "{r["name"]}" annotated by multiple corpus files ({files}) '
                        f'— using the first'
                    )
                corpus = corpus_payload(entries[0][1])

        chapter = (corpus.get('chapter') if corpus and corpus.get('chapter')
                   else chapter_for_file(r['file']))

        uses = sorted({id_to_slug[d] for d in r.get('deps', []) if d in id_to_slug})

        nodes_by_slug[slug] = {
            'slug': slug,
            'id': r['id'],
            'name': r['name'],
            'shortName': r['name'].split('.')[-1],
            'kind': r['kind'],
            'private': bool(r['private']),
            'signature': r.get('signature', ''),
            'doc': r.get('doc', ''),
            'file': r.get('file', ''),
            'startLine': r.get('startLine', 0),
            'endLine': r.get('endLine', 0),
            'chapter': chapter,
            'uses': uses,
            'usedBy': [],
            'collision': is_collision,
            'capstone': r['name'] in CAPSTONE_NAMES,
            'corpus': corpus,
        }

    # Reverse edges.
    for slug, node in nodes_by_slug.items():
        for target in node['uses']:
            if target in nodes_by_slug and target != slug:
                nodes_by_slug[target]['usedBy'].append(slug)
    for node in nodes_by_slug.values():
        node['usedBy'] = sorted(set(node['usedBy']))

    nodes = [nodes_by_slug[s] for s in sorted(nodes_by_slug)]
    annotated = sum(1 for n in nodes if n['corpus'])

    payload = {
        'pin': read_pin(),
        'source': source,
        'has_full_metadata': has_decls,
        'decl_count': len(nodes),
        'annotated_count': annotated,
        'capstones': sorted(n['slug'] for n in nodes if n['capstone']),
        'chapters': chapters,
        'collisions': [
            {
                'name': name,
                'ids': sorted(r['id'] for r in rs),
                'files': sorted(r['file'] for r in rs),
            }
            for name, rs in sorted(collisions.items())
        ],
        'nodes': nodes,
    }

    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SITE_DATA_DIR / 'nodes.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    print(f'Wrote {out_path} ({out_path.stat().st_size // 1024} KiB, '
          f'{len(nodes)} nodes, {annotated} annotated)')

    if collisions:
        print(f'Collision groups (corpus join deferred to notes#7): {len(collisions)} '
              f'({sum(len(v) for v in collisions.values())} decls)')
        for name in sorted(collisions):
            print(f'  - {name}')

    if warnings:
        print(f'\n{len(warnings)} warning(s):')
        for w in warnings:
            print(f'  WARN: {w}')

    if not args.no_coverage:
        cov = subprocess.run(
            [sys.executable, str(REPO_ROOT / 'scripts' / 'coverage.py'), '--json-only'],
            cwd=str(REPO_ROOT),
        )
        if cov.returncode != 0:
            sys.exit('ERROR: coverage.py failed')


if __name__ == '__main__':
    main()
