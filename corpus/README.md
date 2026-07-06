# corpus/

Per-declaration annotation YAML files.

## Layout

```
corpus/<module-path>/<decl-name>.yaml
```

The `<module-path>` mirrors the Lean module path with `.` replaced by `/`.
For example, the declaration `LerayHopf.R3.rellich_seq_compact` lives at:

```
corpus/LerayHopf/R3/rellich_seq_compact.yaml
```

## Schema

See `docs/schemas/corpus.schema.json` for the full JSON Schema (draft-07).

Key fields:
- `name` — fully-qualified Lean declaration name
- `tier` — `full` (statement + proof + gap) or `gloss` (1–3 line role summary)
- `statement_ja` — Japanese translation of the mathematical statement
- `proof_ja` — Japanese proof narrative (required for `tier: full` theorems)
- `gap` — formalization gap assessment (`none | mild | large`)
- `chapter` — chapter assignment from `docs/schemas/chapters.yaml`
- `tags` — optional free-form tags

## Naming

Corpus files use the declaration's **simple name** (last component) as the filename.
The fully-qualified name is stored in the `name` field for join against `extracted/`.

## 数式記法（KaTeX）

`statement_ja` と `proof_ja` の本文では TeX 数式を書ける。サイトはビルド時に
vendored KaTeX でレンダリングする（CDN 不使用）。

- **インライン**: `$ ... $` — 例: `発散ゼロな初期値 $u_0 \in L^2_\sigma(\mathbb{R}^3)$`
- **ディスプレイ**: `$$ ... $$` — 中央寄せの別行立て数式

規約:

- YAML はブロックスカラー（`statement_ja: |`）で書くこと。バックスラッシュがそのまま
  KaTeX に渡る（プレーンスカラーだとエスケープ解釈でずれる）。
- `$` を数式以外（通貨など）で使うときはレンダリングされるので避けるか `\$` を使う。
- KaTeX 未対応のコマンドは避ける（サイトは `throwOnError:false` で失敗時は生テキスト表示）。
