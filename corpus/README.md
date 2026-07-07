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
- `file` — source path from `extracted/decls.json`; optional for unique names, required when the
  same display `name` appears in more than one declaration
- `tier` — `full` (statement + proof + gap) or `gloss` (1–3 line role summary)
- `statement_ja` — Japanese translation of the mathematical statement
- `proof_ja` — Japanese proof narrative (required for `tier: full` theorems)
- `gap` — formalization gap assessment (`none | mild | large`)
- `chapter` — chapter assignment from `docs/schemas/chapters.yaml`
- `tags` — optional free-form tags

## Naming

Corpus files use the declaration's **simple name** (last component) as the filename.
The fully-qualified name is stored in the `name` field for join against `extracted/`.

## 執筆規約（notes#12 v1.1 — 組版・レジスタ）

owner の v1 実見レビューを反映した凍結規約。`scripts/prose_lint.py` が pre-commit /
CI で機械チェックする（D1・D2 の Lean 名・D5 は**ハードエラー**、長すぎるインライン
数式は警告）。

### D1. 段落と物理改行

- **prose フィールド（`statement_ja` / `proof_ja` / `gap.note`）は 1 段落 = 1 物理行で書く。**
  段落内で折り返さない。空行が段落区切りになる。
- レンダラは空行で `<p>` に分割し、幅・高さ・文字数に基づく切断は**一切しない**。
  ホームカードは第 1 段落全文、ホバーカードは予算内最後の「。」までを表示する
  （どちらも文の途中では切らない）。

### D2. 数式

- 長い／重い数式（インラインで全角換算 ~20 字超、または分数・総和・複数関係子を含む）は
  **ディスプレイ数式 `$$ ... $$`** にする。
- **数式内に Lean 宣言名を書かない。** `\mathrm{divTestFunctional}` のような camelCase・
  アンダースコアを含む名前は禁止。標準の数学記法と意訳語で書く（例: 「発散記号」「粘性形式」）。

### D3. 自然言語のレジスタ（文体）

- `statement_ja` / `proof_ja` は**通常の数学論文・書籍の文体**のみ。Lean 宣言名・
  「構造体」「フィールド」「インスタンス」等の Lean 用語・tactic 名を出さない。
- Lean 固有の注意（総和規約・代表元・インスタンス解決・mathlib 補題名など）は
  `gap.note` に書く。`gap.note` 内では mathlib 補題名を `` `code` `` で表してよい。

### D5. インライン記法

レンダラが対応するのは次のインライン記法と KaTeX 数式のみ。それ以外の markdown
（見出し・リスト・リンク・引用）は非対応で lint がブロックする。

- `` `code` `` → 等幅（gap.note で mathlib 補題名などに使う）
- `**強調**` → ボールド
- `[[表示語]]` / `[[表示語|宣言名または slug]]` → 下線付きの参照。ホバーで定義カード、
  クリックでそのノードへ遷移する。「証明を読んでいて気になったら開ける便利メモ」。
  `|` を省くと表示語を display name として解決する。**意訳語からでも対応する Lean 定義に
  届かせるための記法。** 参照先は `extracted/decls.json` に実在する宣言名にすること。

## 数式記法（KaTeX）

`statement_ja` と `proof_ja` の本文では TeX 数式を書ける。サイトはビルド時に
vendored KaTeX でレンダリングする（CDN 不使用）。

- **インライン**: `$ ... $` — 例: `発散ゼロな初期値 $u_0 \in L^2_\sigma(\mathbb{R}^3)$`
- **ディスプレイ**: `$$ ... $$` — 中央寄せの別行立て数式

規約:

- YAML はブロックスカラー（`statement_ja: |`）で書くこと。バックスラッシュがそのまま
  KaTeX に渡る（プレーンスカラーだとエスケープ解釈でずれる）。
- 各段落は 1 物理行に収める（D1）。ディスプレイ数式も 1 行で書く。
- `$` を数式以外（通貨など）で使うときはレンダリングされるので避けるか `\$` を使う。
- KaTeX 未対応のコマンドは避ける（サイトは `throwOnError:false` で失敗時は生テキスト表示）。
