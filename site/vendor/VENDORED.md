# Vendored third-party assets

The site is fully self-contained: no CDN, no bundler, no npm at runtime. The only
vendored dependency is KaTeX (math rendering). It is downloaded **once at build time**
and committed here so the site runs from a bare `python3 -m http.server` with no network.

## KaTeX

- **Version:** `0.17.0`
- **Source:** npm tarball `https://registry.npmjs.org/katex/-/katex-0.17.0.tgz`
- **License:** MIT (see the KaTeX project)
- **Files vendored** into `site/vendor/katex/`:
  - `katex.min.js` — core renderer
  - `katex.min.css` — styles (references `fonts/` by relative URL)
  - `auto-render.min.js` — the `renderMathInElement` contrib extension
  - `fonts/` — the KaTeX web fonts referenced by `katex.min.css`

### Re-vendoring

```bash
ver=0.17.0
curl -sSL -o /tmp/katex.tgz "https://registry.npmjs.org/katex/-/katex-$ver.tgz"
tar -C /tmp -xzf /tmp/katex.tgz
cp /tmp/package/dist/katex.min.js         site/vendor/katex/
cp /tmp/package/dist/katex.min.css        site/vendor/katex/
cp /tmp/package/dist/contrib/auto-render.min.js site/vendor/katex/
cp -r /tmp/package/dist/fonts/.           site/vendor/katex/fonts/
```

Bump the version number here and in the re-vendoring command together.
