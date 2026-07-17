# site/

Pure-static interactive viewer. No framework, no bundler, no npm at runtime; the only
vendored dependency is KaTeX (see `vendor/VENDORED.md`).

## Structure

```
site/
  index.html            entry point
  app.js                vanilla JS SPA (hash routing, all rendering client-side)
  styles.css
  vendor/
    VENDORED.md          how KaTeX was vendored (version + re-vendor commands)
    katex/               katex.min.js + katex.min.css + auto-render.min.js + fonts/
  data/
    .gitkeep             preserves directory (generated JSON is not committed)
    nodes.json           built by scripts/build_site_data.py (decls ⋈ corpus, no source bodies)
    sources.json         built by scripts/build_site_data.py (verbatim Lean source, lazy-loaded)
    coverage.json        built by scripts/coverage.py
    
**Note:** `site/data/*.json` files are generated artifacts, not source-reviewed files.
They are produced locally via `build_site_data.py` and in CI via `.github/workflows/ci.yml`.
During Phase A (pre-publication), generated JSON is uploaded as workflow artifacts for inspection
but not deployed to Pages. Phase B will enable public Pages deployment after the public-readiness gate.
```

## License scope

The site viewer code is licensed as a software component under Apache-2.0. Mathematical
explanations, annotations, and prose content rendered by the viewer are licensed under
CC-BY-4.0 unless otherwise noted. Generated `site/data/*.json` files are derived artifacts,
not source-reviewed material; downstream users should observe the licenses of the Lean
source and annotation/prose inputs from which they were generated. Vendored third-party
assets under `site/vendor/` (currently KaTeX, MIT) carry their own upstream license — see
`site/vendor/VENDORED.md` and `site/vendor/katex/LICENSE` — and are not covered by the
Apache-2.0/CC-BY-4.0 split above. See the root `LICENSE.md` for the full, authoritative
per-path scope.

## Build & preview

### Local build

**Important:** After a fresh clone, `site/data/*.json` files do not exist (they are gitignored).
You must run `build_site_data.py` before serving the site.

```bash
# from repo root — build site data first
# Option 1: with verbatim Lean source (requires leray-hopf checkout at extracted/PIN)
python3 scripts/build_site_data.py --lean-root /path/to/leray-hopf
# -> site/data/nodes.json (with has_source:true) + site/data/sources.json (populated)

# Option 2: without leray-hopf checkout (source-less build)
python3 scripts/build_site_data.py
# -> site/data/nodes.json (with has_source:false) + site/data/sources.json (empty stub)

# Then serve (any static server; no build step, no server-side code)
cd site && python3 -m http.server 8000
# open http://localhost:8000/
```

### CI build workflow (Phase A)

`.github/workflows/ci.yml` runs on every push and PR, as three jobs (the last one
gated on the first two passing, via `needs:`, rather than re-running their checks):

1. `validate` — corpus/glossary/prose lint, coverage report, and a structure-only
   `scripts/build_site_data.py` run
2. `render-tests` — `npm test` (jsdom render harness)
3. `build-artifact` — builds site data **without `--lean-root`** (leray-hopf is private
   during Phase A), generates a size report with `scripts/site_data_size_report.py`,
   and uploads the entire `site/` directory as a workflow artifact

The workflow does **not** deploy to Pages during Phase A. Generated JSON remains
uncommitted and is available only as workflow artifacts for pre-publication inspection.

**Current limitation:** Phase A CI produces only source-less artifacts (`has_source:false`,
empty `sources.json`). Before enabling Phase B public deployment, a source-enabled build
(`--lean-root` with leray-hopf at `extracted/PIN`) must be inspected locally to verify:
- No private paths, agent notes, or internal-only content in generated JSON
- Source extraction correctness for all 1,412 declarations
- Size report within budget when source bodies are included

**Phase B** (after public-readiness gate and source-enabled inspection):
- Add leray-hopf checkout at `extracted/PIN` in the workflow
- Pass `--lean-root` to `build_site_data.py` for source-enabled builds
- Enable Pages deployment step

### Source-enabled builds

To include verbatim Lean source in the site, `build_site_data.py` requires
`--lean-root <path>` pointing to a checkout of `uda-lab/leray-hopf` at the commit
specified in `extracted/PIN`. The script extracts source text from the Lean files
and populates `sources.json` for lazy loading.

Without `--lean-root`, the site still works but shows file:line references instead
of embedded source code.

`build_site_data.py` shells out to `coverage.py` by default, so a single invocation
refreshes both data files. Flags: `--no-coverage` (skip coverage refresh),
`--out <path>` (write nodes.json elsewhere; the paired `sources.json` is written next
to it unless `--sources-out` is supplied). The committed data is built **with**
`--lean-root`, so the site can lazy-load verbatim Lean source per declaration without
embedding source bodies in the initial `nodes.json` payload.

## Data flow

```
extracted/decls.json (or names-fallback.json)  +  corpus/**/*.yaml
        → scripts/build_site_data.py → site/data/nodes.json
                                     → site/data/sources.json
        → scripts/coverage.py        → site/data/coverage.json
                                      ↓
                          site/app.js loads static JSON files
```

The site loads `nodes.json` and `coverage.json` up front. It fetches `sources.json`
only when a declaration source panel is opened. Adding annotations (S3 seed) is
purely a corpus + rebuild operation — **no site code changes required**.

## Routes (hash-based)

- `#/` — home (2 capstone cards, coverage summary, chapter list)
- `#/chapter/<id>` — chapter page (defs group / theorems group; private helpers folded per file)
- `#/decl/<slug>` — declaration node page (Lean ⇄ Japanese, uses accordion, used-by, DAG links)
- `#/dag` — proof tree, progressive disclosure from the 2 capstone roots
- `#/coverage` — per-chapter × per-tier coverage table
- `#/search/<query>` — name (prefix) + statement_ja (substring) search, grouped by kind

`slug` is the display name when unique, else the declaration `id` (the 8 private-helper
name collisions; corpus join for those is deferred to notes#7).

## Graceful degradation

- **Empty corpus** — every node renders from extracted metadata with `未注釈` placeholders.
- **No `decls.json`** — falls back to `names-fallback.json` (skeleton: names/kinds/files,
  no signatures or dependency edges; `has_full_metadata: false`).
- **No `--lean-root`** — nodes carry `has_source: false` and `sources.json` is empty;
  the proof band shows the doc-comment + `file:startLine–endLine` reference instead
  of the Lean body.
