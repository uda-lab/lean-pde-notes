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
    nodes.json           built by scripts/build_site_data.py (decls ⋈ corpus, no source bodies)
    sources.json         built by scripts/build_site_data.py (verbatim Lean source, lazy-loaded)
    coverage.json        built by scripts/coverage.py
```

## Build & preview

```bash
# from repo root — embed verbatim Lean source (needs a lean-pde checkout at the PIN commit)
python3 scripts/build_site_data.py --lean-root /workspaces/lean-pde
# -> site/data/nodes.json + site/data/sources.json

# without a lean-pde checkout, source is omitted (has_source:false) and the proof band
# falls back to the doc-comment + file:line reference:
python3 scripts/build_site_data.py
# -> site/data/nodes.json + empty site/data/sources.json

# serve (any static server; no build step, no server-side code)
cd site && python3 -m http.server 8000
# open http://localhost:8000/
```

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
