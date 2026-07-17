#!/usr/bin/env python3
"""
build_site_data.py — join extracted declaration metadata with the annotation corpus
into a single static JSON payload for the site/ viewer.

Inputs
  extracted/decls.json          (preferred) full metadata: id, name, kind, private,
                                signature, doc, file, startLine, endLine, deps[id-refs]
  extracted/names-fallback.json (fallback)  name, kind, file, line   — skeleton only
  extracted/PIN                 40-char lean-pde SHA (recorded into the output)
  corpus/**/*.yaml              per-declaration annotations (joined by display name;
                                colliding names require file metadata)
  docs/schemas/chapters.yaml    chapter taxonomy (ids + Japanese labels)

Output
  site/data/nodes.json          deterministic metadata/annotation payload loaded up front.
  site/data/sources.json        optional verbatim Lean source payload loaded on demand.
  site/data/coverage.json       refreshed by shelling out to scripts/coverage.py.

Join model
  * `deps` edges reference declaration **ids** (unique). Nodes are keyed by a URL
    **slug**: the display `name` when that name is unique in the universe, else the
    (always-unique) `id`. This keeps slugs readable for the common case while staying
    unambiguous for declaration name collisions.
  * The corpus is keyed by display `name` for unique names. When a name belongs to a
    collision group (see notes#7), the corpus YAML must carry `file`; the join resolves
    name -> file -> stable declaration id.

Source embedding
  With --lean-root <path> (a checkout of lean-pde at the PIN commit), each record's
  verbatim declaration text (startLine..endLine, exactly as scripts/workpacket.py reads
  it) is written to sources.json keyed by node slug, while nodes.json carries only
  `has_source: true`. Without --lean-root, sources.json is empty and nodes carry
  `has_source: false`; the viewer falls back to the doc-comment + file:line reference.

Determinism: nodes are sorted by slug, edge lists are sorted, and json.dump uses
sort_keys=True so the committed output diffs cleanly.

Usage:
    python3 scripts/build_site_data.py --lean-root /workspaces/lean-pde
    python3 scripts/build_site_data.py --no-coverage   # skip coverage.py refresh
    python3 scripts/build_site_data.py --out /tmp/x.json --no-coverage  # also writes /tmp/sources.json
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit('ERROR: PyYAML required. pip install pyyaml')

sys.path.insert(0, str(Path(__file__).parent))
from bibliography import parse_bibliography  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
EXTRACTED_DIR = REPO_ROOT / 'extracted'
CORPUS_DIR = REPO_ROOT / 'corpus'
SITE_DATA_DIR = REPO_ROOT / 'site' / 'data'
CITATION_PATH = REPO_ROOT / 'CITATION.cff'
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
    ('/Galerkin/', 'galerkin-generic'),
    ('R3/GalerkinODECapstone', 'capstone-r3'),
    ('R3/SolutionInterfaces', 'capstone-r3'),
    ('Torus/GalerkinODECapstone', 'capstone-torus'),
    ('Torus/SolutionInterfaces', 'capstone-torus'),
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
    ('Torus/Leray.lean', 'projections-galerkin'),
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
    'LerayHopf.exists_lerayHopf_r3',
    'LerayHopf.exists_lerayHopf_torus3',
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


def find_corpus_for_record(rec: dict, entries: list[tuple[Path, dict]], is_collision: bool,
                           warnings: list[str]) -> dict | None:
    if not entries:
        return None
    if is_collision:
        matched = [(p, d) for p, d in entries if d.get('file') == rec.get('file')]
        if not matched:
            return None
        if len(matched) > 1:
            files = ', '.join(str(p.relative_to(REPO_ROOT)) for p, _ in matched)
            warnings.append(
                f'collision record "{rec["name"]}" in {rec.get("file", "")} annotated '
                f'by multiple corpus files ({files}) — using the first'
            )
        return matched[0][1]

    if len(entries) > 1:
        files = ', '.join(str(p.relative_to(REPO_ROOT)) for p, _ in entries)
        warnings.append(
            f'name "{rec["name"]}" annotated by multiple corpus files ({files}) '
            f'— using the first'
        )
    return entries[0][1]


def corpus_payload(doc: dict) -> dict:
    """Project a corpus YAML into the site-facing shape (sample flag derived from tags).

    `proof_status` defaults to 'verified' when absent from the corpus YAML (notes#65: no
    known literal `sorry`, no known false/over-general statement, not a historical scaffold
    or retired declaration). The payload always carries an explicit value so the UI never
    has to special-case a missing field.
    """
    tags = doc.get('tags') or []
    payload = {
        'tier': doc.get('tier'),
        'statement_ja': doc.get('statement_ja', ''),
        'gap': doc.get('gap') or {'level': 'none'},
        'chapter': doc.get('chapter'),
        'tags': tags,
        'sample': 'sample' in tags,
        'proof_status': doc.get('proof_status') or 'verified',
    }
    if doc.get('proof_ja'):
        payload['proof_ja'] = doc['proof_ja']
    if doc.get('references'):
        payload['references'] = doc['references']
    return payload


def read_pin() -> str:
    pin_path = EXTRACTED_DIR / 'PIN'
    if pin_path.exists():
        return pin_path.read_text(encoding='utf-8').strip()
    return ''


def read_citation_meta(pin: str, warnings: list) -> dict:
    """Project CITATION.cff into the site-facing "release metadata" shape (notes#68):
    author, citation/license targets, and the source repository this corpus/site is
    pinned to. CITATION.cff is the single source of truth; this avoids hand-duplicating
    author/license/source-repo strings into the site build.

    Cross-checks CITATION.cff's `references[0].commit` against `extracted/PIN` and
    appends a build warning on mismatch — the exact class of bug (a manually-maintained
    pin silently drifting from the real source) that notes#66 caught by hand once.
    """
    if not CITATION_PATH.exists():
        return {}
    with open(CITATION_PATH, encoding='utf-8') as f:
        cff = yaml.safe_load(f)
    if not isinstance(cff, dict):
        return {}
    authors = [
        ' '.join(filter(None, [a.get('given-names'), a.get('family-names')]))
        for a in (cff.get('authors') or []) if isinstance(a, dict)
    ]
    refs = cff.get('references')
    source = refs[0] if isinstance(refs, list) and refs and isinstance(refs[0], dict) else {}
    source_commit = source.get('commit', '')
    if pin and source_commit and pin != source_commit:
        warnings.append(
            f'WARNING: CITATION.cff references[0].commit ({source_commit}) does not '
            f'match extracted/PIN ({pin}) — the next repin PR must update CITATION.cff too'
        )
    return {
        'authors': authors,
        'repository_code': cff.get('repository-code', ''),
        'license': cff.get('license'),
        'license_url': cff.get('license-url', ''),
        'source_repository': source.get('repository-code', ''),
        'source_commit': source_commit,
    }


class SourceReader:
    """Read verbatim declaration text from a lean-pde checkout (workpacket.py style:
    1-based startLine..endLine inclusive). Caches each file's lines. No-op when the
    lean-root is not provided or a file/range is missing."""

    def __init__(self, lean_root):
        self.root = Path(lean_root) if lean_root else None
        self._cache: dict[str, list[str] | None] = {}
        self.hits = 0
        self.misses = 0

    def _lines(self, rel_file):
        if rel_file not in self._cache:
            path = self.root / rel_file if self.root else None
            if path and path.is_file():
                self._cache[rel_file] = path.read_text(encoding='utf-8', errors='replace').splitlines()
            else:
                self._cache[rel_file] = None
        return self._cache[rel_file]

    def source_for(self, rec):
        if not self.root:
            return None
        lines = self._lines(rec.get('file', ''))
        start, end = rec.get('startLine', 0), rec.get('endLine', 0)
        if not lines or start < 1 or end < start or end > len(lines):
            self.misses += 1
            return None
        self.hits += 1
        return '\n'.join(lines[start - 1:end])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-coverage', action='store_true',
                        help='Do not shell out to coverage.py')
    parser.add_argument('--lean-root', default=None,
                        help='Path to a lean-pde checkout at the PIN commit; embed verbatim source')
    parser.add_argument('--out', default=None,
                        help='Output path for nodes.json (default site/data/nodes.json)')
    parser.add_argument('--sources-out', default=None,
                        help='Output path for sources.json (default next to nodes.json)')
    args = parser.parse_args()

    records, universe_source, has_decls = load_universe()
    if not records:
        sys.exit('ERROR: no name universe (extracted/decls.json or names-fallback.json).')
    print(f'Universe: {len(records)} records from {universe_source}')

    reader = SourceReader(args.lean_root)
    if args.lean_root:
        print(f'Embedding source from lean-root: {args.lean_root}')

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

    # Collision names are joinable only when the corpus entry carries a matching source `file`.
    for name, entries in sorted(corpus_by_name.items()):
        if name in collisions:
            valid_files = {r.get('file', '') for r in collisions[name]}
            for fpath, doc in entries:
                file = doc.get('file')
                if not file:
                    warnings.append(
                        f'corpus {fpath.relative_to(REPO_ROOT)} targets collision name '
                        f'"{name}" ({len(collisions[name])} decls) without file — not joinable'
                    )
                elif file not in valid_files:
                    choices = ', '.join(sorted(valid_files))
                    warnings.append(
                        f'corpus {fpath.relative_to(REPO_ROOT)} targets collision name '
                        f'"{name}" with file "{file}", which is not in {universe_source}; '
                        f'expected one of: {choices}'
                    )

    # Build nodes and the separate source payload.
    nodes_by_slug: dict[str, dict] = {}
    sources_by_slug: dict[str, str] = {}
    for r in records:
        slug = slug_of(r)
        is_collision = r['name'] in collisions

        corpus_doc = find_corpus_for_record(
            r, corpus_by_name.get(r['name'], []), is_collision, warnings
        )
        corpus = corpus_payload(corpus_doc) if corpus_doc else None

        chapter = (corpus.get('chapter') if corpus and corpus.get('chapter')
                   else chapter_for_file(r['file']))

        uses = sorted({id_to_slug[d] for d in r.get('deps', []) if d in id_to_slug})

        src = reader.source_for(r)
        if src is not None:
            sources_by_slug[slug] = src
        node = {
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
            'has_source': src is not None,
            'corpus': corpus,
        }
        nodes_by_slug[slug] = node

    # Reverse edges.
    for slug, node in nodes_by_slug.items():
        for target in node['uses']:
            if target in nodes_by_slug and target != slug:
                nodes_by_slug[target]['usedBy'].append(slug)
    for node in nodes_by_slug.values():
        node['usedBy'] = sorted(set(node['usedBy']))

    nodes = [nodes_by_slug[s] for s in sorted(nodes_by_slug)]
    annotated = sum(1 for n in nodes if n['corpus'])

    # notes#65: corpus-wide proof_status tally, independent of `tier`/gap. Annotated-only
    # (an unannotated declaration has no corpus.proof_status to report); used by the site
    # to enumerate every non-verified declaration alongside the structural coverage stat,
    # so "100% annotated" is never conflated with "100% proved".
    proof_status_counts: dict[str, int] = {}
    for n in nodes:
        if n['corpus']:
            status = n['corpus']['proof_status']
            proof_status_counts[status] = proof_status_counts.get(status, 0) + 1

    out_path = Path(args.out) if args.out else (SITE_DATA_DIR / 'nodes.json')
    sources_out_path = (
        Path(args.sources_out)
        if args.sources_out
        else out_path.with_name('sources.json')
    )

    pin = read_pin()
    bibliography = {cid: info['citation'] for cid, info in parse_bibliography().items()}
    payload = {
        'pin': pin,
        'built_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'citation': read_citation_meta(pin, warnings),
        'bibliography': bibliography,
        'universe_source': universe_source,
        'has_full_metadata': has_decls,
        'has_source': reader.hits > 0,
        'source_count': reader.hits,
        'source_payload': sources_out_path.name,
        'decl_count': len(nodes),
        'annotated_count': annotated,
        'proof_status_counts': proof_status_counts,
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

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    sources_payload = {
        'pin': pin,
        'source_count': len(sources_by_slug),
        'sources': {slug: sources_by_slug[slug] for slug in sorted(sources_by_slug)},
    }
    sources_out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sources_out_path, 'w', encoding='utf-8') as f:
        json.dump(sources_payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    print(f'Wrote {out_path} ({out_path.stat().st_size // 1024} KiB, '
          f'{len(nodes)} nodes, {annotated} annotated, {reader.hits} with source)')
    print(f'Wrote {sources_out_path} ({sources_out_path.stat().st_size // 1024} KiB, '
          f'{len(sources_by_slug)} source entries)')
    if args.lean_root and reader.misses:
        print(f'  ({reader.misses} records had no readable source range)')

    if collisions:
        print(f'Collision groups: {len(collisions)} '
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
