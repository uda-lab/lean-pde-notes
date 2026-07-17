# License

Unless otherwise noted, this repository uses split licensing:

- Software components are licensed under the Apache License 2.0. This includes
  site viewer code, scripts, tests, CI/workflow configuration, and other
  implementation or tooling files.

- Mathematical explanations, annotations, and prose content are licensed under
  Creative Commons Attribution 4.0 International (CC BY 4.0). This includes
  `corpus/**/*.yaml` prose fields, documentation prose where applicable, and
  explanatory text intended as educational or scholarly content.

- Generated site data under `site/data/` is not source material. `site/data/nodes.json`
  is a join of Lean declaration metadata and the annotation corpus (see the two
  bullets above for the license of each input). `site/data/sources.json` embeds
  verbatim Lean source text from the companion [`lean-pde`](https://github.com/uda-lab/lean-pde)
  repository (Apache-2.0); it is not this repository's own software, and
  downstream users should observe `lean-pde`'s license for that content, not this
  repository's Apache-2.0 grant.

- Vendored third-party assets under `site/vendor/` are licensed by their upstream
  projects, not by this repository's split above. Currently this is KaTeX
  (MIT, Copyright (c) 2013-2020 Khan Academy and other contributors); the full
  upstream license text is included at `site/vendor/katex/LICENSE`, and
  provenance/checksums are recorded in `site/vendor/VENDORED.md`.

The canonical license identifiers are:

- Apache-2.0: <https://www.apache.org/licenses/LICENSE-2.0>
- CC-BY-4.0: <https://creativecommons.org/licenses/by/4.0/legalcode>
- MIT (vendored KaTeX only): <https://opensource.org/license/mit/>, full text at
  `site/vendor/katex/LICENSE`

See [`CITATION.cff`](CITATION.cff) for how to cite this repository and the
companion `lean-pde` formalization it annotates.

This licensing notice does not attempt to license mathematical facts or theorems
themselves.

