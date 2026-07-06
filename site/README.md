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
    nodes.json           built by scripts/build_site_data.py (decls ⋈ corpus)
    coverage.json        built by scripts/coverage.py
```

## Build & preview

```bash
# from repo root
python3 scripts/coverage.py            # -> site/data/coverage.json
python3 scripts/build_site_data.py     # -> site/data/nodes.json (also refreshes coverage)

# serve (any static server; no build step, no server-side code)
cd site && python3 -m http.server 8000
# open http://localhost:8000/
```

`build_site_data.py` shells out to `coverage.py` by default, so a single invocation
refreshes both data files. Pass `--no-coverage` to skip that.

## Data flow

```
extracted/decls.json (or names-fallback.json)  +  corpus/**/*.yaml
        → scripts/build_site_data.py → site/data/nodes.json
        → scripts/coverage.py        → site/data/coverage.json
                                      ↓
                          site/app.js loads both as static JSON
```

The site reads only these two JSON files. Adding annotations (S3 seed) is purely a
corpus + rebuild operation — **no site code changes required**.

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
