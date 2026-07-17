# leray-hopf-notes — 証明掘り下げインタラクティブノート

[uda-lab/leray-hopf](https://github.com/uda-lab/leray-hopf)（Leray–Hopf 弱解存在の Lean 4 + mathlib
形式化、kernel-only 達成済み）の**全宣言対訳解説サイト**の作業リポジトリ。宣言数は固定値では
なく `extracted/decls.json`（コミット済み、正典の名前 universe）で確認できる — 現在の値は
`python3 scripts/coverage.py` または `jq length extracted/decls.json` で取得可能。

Lean コードと「自然な日本語の数学証明として読める文章」を並置し、ホバー定義カード・
1 段アコーディオン展開・リンクナビゲーションで宣言依存グラフを capstone から末端まで
辿れる純静的 UI（`site/`、実装済み）を構築する。

**Issues**: [#63 公開前 repo/site 監査 follow-up（優先度別 umbrella）](../../issues/63) — 現行の
作業はこの umbrella の subissue を参照。初期設計は [#1](../../issues/1)（進行中）に、抽出スパイク
[#2](../../issues/2) とハーネス整備 [#3](../../issues/3) は完了済み（クローズ済み、履歴として参照）。

## リポジトリ構成

```
corpus/           宣言ごとの注釈 YAML（statement_ja / proof_ja / gap note / chapter）
                  layout: corpus/<モジュールパス>/<宣言名>.yaml
extracted/        機械抽出 JSON（leray-hopf の warm ビルドから生成、コミット済み）
  names-fallback.json  静的 walk による名前 universe（decls.json 欠落時のフォールバック、
                        意図的に unrefresh のスケルトン — decls.json が正典）
  decls.json      lake exe extract_notes が生成するフル宣言メタデータ（コミット済み・正典）
  PIN             抽出元 leray-hopf コミット SHA（decls.json 使用時必須）
site/             純静的ビューア（実装済み — vanilla JS SPA、ビルド不要・フレームワーク不要）
  data/           生成物（gitignored）。nodes.json / sources.json は build_site_data.py が、
                  coverage.json は coverage.py が生成する
scripts/          ツール群（Lean ビルド不要、数秒で完走）
  count_decls.py       名前 universe 生成（fallback）
  validate.py          YAML スキーマ検査 + corpus ⊆ universe
  coverage.py          章別・tier 別・proof_status 別カバレッジ集計
  build_site_data.py   decls.json ⋈ corpus → site/data/nodes.json + sources.json
  workpacket.py        翻訳作業パケット生成
  glossary_lint.py     用語集違反チェック
  prose_lint.py        表記規則チェック（段落・数式内 Lean 識別子・非対応記法）
  check_docs.py        living docs に宣言数・衝突数のハードコードが無いか検査（notes#71）
  hooks/pre-commit     Git フック
docs/
  GLOSSARY.md          英日用語集
  schemas/
    corpus.schema.json  YAML スキーマ（JSON Schema draft-07）
    chapters.yaml        章タクソノミー
```

## パイプライン

```
leray-hopf (warm build)
    ↓ lake exe extract_notes
extracted/decls.json           (コミット済み・正典の名前 universe)
extracted/names-fallback.json  (コミット済みフォールバック — decls.json 欠落時のみ使用)
         ↓
corpus/**/*.yaml  ←─ 翻訳ワーカー（workpacket.py が作業パケットを生成）
         ↓
scripts/validate.py        → pass/fail（schema + corpus ⊆ universe）
scripts/glossary_lint.py   → 訳語チェック
scripts/prose_lint.py      → 表記規則チェック
scripts/coverage.py        → site/data/coverage.json
         ↓
scripts/build_site_data.py → site/data/nodes.json + site/data/sources.json
         ↓
site/  (静的ビューア — 任意の静的サーバで配信、ビルド不要)
```

## クイックスタート

```bash
# 1. フックを有効化（初回のみ）
git config core.hooksPath scripts/hooks

# 2. 依存インストール
pip install pyyaml jsonschema
npm ci

# 3. corpus を検証
python3 scripts/validate.py

# 4. カバレッジ確認
python3 scripts/coverage.py

# 5. 作業パケット生成（例: R3 主定理の未注釈宣言）
python3 scripts/workpacket.py --chapter capstone-r3 --lean-root /path/to/leray-hopf

# 6. 名前 universe を再生成（leray-hopf が手元にある場合。通常は不要 — decls.json が正典）
python3 scripts/count_decls.py /path/to/leray-hopf

# 7. サイトデータを生成してプレビュー
python3 scripts/build_site_data.py
cd site && python3 -m http.server 8000   # http://localhost:8000/

# 8. サイトのレンダーテスト（jsdom）
npm test
```

## ライセンスと引用

このリポジトリは split licensing を採用する。詳細は [`LICENSE.md`](LICENSE.md) を参照。

- site viewer code、scripts、tests、CI/workflow configuration などの software components は
  Apache License 2.0。
- `corpus/**/*.yaml` の prose fields、documentation prose、教育的・学術的説明文などの
  mathematical explanations / annotations / prose content は Creative Commons Attribution
  4.0 International (CC BY 4.0)。
- `site/data/*.json` は source material ではなく生成物である。Lean source と annotation/prose
  corpus から生成されるため、再利用時は underlying source materials の license scope を確認する。

引用 metadata は [`CITATION.cff`](CITATION.cff) に置いている。この annotated viewer / corpus を
利用する場合は、GitHub の "Cite this repository" または `CITATION.cff` の内容に従う。

## corpus YAML の作り方

`workpacket.py` が出力する雛形を埋める：

```yaml
name: LerayHopf.rellich_seq_compact    # 完全修飾 Lean 名（extracted と同じ）
tier: full                              # full | gloss
statement_ja: |
  H¹ ノルムが一様有界な L²(𝕋³;ℂ) の列は L² 収束部分列をもつ。
proof_ja: |
  Parseval 等式で ‖f‖² = ∑‖f̂(k)‖² を確認し、…
gap:
  level: mild                           # none | mild | large
  # note: |  # large のとき必須
chapter: compactness
tags: [rellich, fourier-tail]
# proof_status: contains-sorry          # 省略時は verified。sorry / 足場 / 廃止 / 隔離中のみ明記
```

tier・gap・proof_status の基準は `docs/schemas/corpus.schema.json` を参照。
用語は `docs/GLOSSARY.md` に準拠。

`statement_ja` / `proof_ja` / `gap.note` は数学内容に限定する。issue/PR 番号・Codex・campaign・
gate・round といった開発プロセス語は任意項目 `provenance` へ書く（サイトでは既定で折りたたまれた
「開発履歴」パネルに表示され、削除はされない）。詳細は notes#69。

## `extracted/decls.json` が有効にする機能

`extracted/decls.json`（正典の名前 universe、コミット済み）が存在することで、以下が有効になる：

- `validate.py` — decls.json の名前セットへチェックし、`extracted/PIN` も検証する
- `workpacket.py` — シグネチャ・doc コメント・依存辺が作業パケットに含まれる
- `coverage.py` / `build_site_data.py` — モジュールパス heuristic に頼らない正確な chapter
  分類・依存グラフ構築ができる

`names-fallback.json` はフォールバックとして残る（`decls.json` が欠落した場合のみ使用される、
名前・kind・file・行番号のみのスケルトン universe）。

## 参照元

- 形式化本体: `uda-lab/leray-hopf` — ローカル clone のパスを `--lean-root` に指定
- 対訳プロトタイプ: leray-hopf の `docs/formalization-review-ja.md`（GLOSSARY の種、ギャップ Note の原型）
