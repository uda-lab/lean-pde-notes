# Vendored third-party assets

The site is fully self-contained: no CDN, no bundler, no npm at runtime. The only
vendored dependency is KaTeX (math rendering). It is downloaded **once at build time**
and committed here so the site runs from a bare `python3 -m http.server` with no network.

## KaTeX

- **Version:** `0.17.0`
- **Upstream project:** <https://katex.org/> / <https://github.com/KaTeX/KaTeX>
- **Source:** npm tarball `https://registry.npmjs.org/katex/-/katex-0.17.0.tgz`
  (sha256 `252efd48f892d178136fe3ba3530d3718b2b087ea81c3a40a877227bc61d5256`)
- **License:** MIT, copyright (c) 2013-2020 Khan Academy and other contributors.
  Full upstream license text is vendored verbatim at `site/vendor/katex/LICENSE`
  (identical to `https://github.com/KaTeX/KaTeX/blob/v0.17.0/LICENSE`); see also
  root `LICENSE.md` for how this fits the repository's file-based split licensing.
- **Files vendored** into `site/vendor/katex/`, with sha256 of the committed files
  (verified to match the upstream `v0.17.0` npm tarball's `dist/` contents):
  - `katex.min.js` — core renderer —
    `45fbe318fea878fdc0a111913dc1f87894b2c439360d0228c086ef313f213efc`
  - `katex.min.css` — styles (references `fonts/` by relative URL) —
    `a34ad8fc188e8f5a3af7ceaa2a58d7210c6c9171335a15bff2b48ebcd6a6f5b0`
  - `auto-render.min.js` — the `renderMathInElement` contrib extension —
    `e5372d199bcdae8b4de71d0f7ceba72a4ba12774a27c60a6f1f77d03b3228ee4`
  - `fonts/` — the KaTeX web fonts referenced by `katex.min.css` (not individually
    checksummed here; re-vendor with the command below to refresh them)
  - `LICENSE` — upstream MIT license text, copied verbatim (not part of the
    `dist/` tarball; fetched from the upstream repository at the pinned tag)

### Re-vendoring

```bash
ver=0.17.0
curl -sSL -o /tmp/katex.tgz "https://registry.npmjs.org/katex/-/katex-$ver.tgz"
tar -C /tmp -xzf /tmp/katex.tgz
cp /tmp/package/dist/katex.min.js         site/vendor/katex/
cp /tmp/package/dist/katex.min.css        site/vendor/katex/
cp /tmp/package/dist/contrib/auto-render.min.js site/vendor/katex/
cp -r /tmp/package/dist/fonts/.           site/vendor/katex/fonts/
curl -sSL -o site/vendor/katex/LICENSE "https://raw.githubusercontent.com/KaTeX/KaTeX/v$ver/LICENSE"
sha256sum site/vendor/katex/katex.min.js site/vendor/katex/katex.min.css \
  site/vendor/katex/auto-render.min.js
```

Bump the version number here and in the re-vendoring command together, and update
the recorded checksums above from the `sha256sum` output.
