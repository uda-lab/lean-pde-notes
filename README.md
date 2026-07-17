# leray-hopf-notes — 証明掘り下げインタラクティブノート

[uda-lab/leray-hopf](https://github.com/uda-lab/leray-hopf)（Leray–Hopf 弱解存在の Lean 4 + mathlib
形式化、kernel-only 達成済み、1,413 宣言）の**全宣言対訳解説サイト**の作業リポジトリ。

Lean コードと「自然な日本語の数学証明として読める文章」を並置し、ホバー定義カード・
1 段アコーディオン展開・リンクナビゲーションで証明ツリーを capstone から末端まで
辿れる純静的 UI を構築する。

**Issues**: [#1 設計・キャンペーン計画](../../issues/1) / [#2 抽出スパイク S0](../../issues/2) / [#3 S1 ハーネス](../../issues/3)

## リポジトリ構成

```
corpus/           宣言ごとの注釈 YAML（statement_ja / proof_ja / gap note / chapter）
                  layout: corpus/<モジュールパス>/<宣言名>.yaml
extracted/        機械抽出 JSON（leray-hopf の warm ビルドから生成）
  names-fallback.json  静的 walk による名前 universe（1,413 件）
  decls.json      S0 が生成するフル宣言メタデータ（未コミット）
  PIN             抽出元 leray-hopf コミット SHA（decls.json 使用時必須）
site/             純静的ビューア（S2 で実装予定）
  data/coverage.json  coverage.py が生成
scripts/          ツール群（Lean ビルド不要、数秒で完走）
  count_decls.py       名前 universe 生成（fallback）
  validate.py          YAML スキーマ検査 + corpus ⊆ universe
  coverage.py          章別・tier 別カバレッジ集計
  workpacket.py        翻訳作業パケット生成
  glossary_lint.py     用語集違反チェック
  hooks/pre-commit     Git フック
docs/
  GLOSSARY.md          英日用語集（~40 エントリ）
  schemas/
    corpus.schema.json  YAML スキーマ（JSON Schema draft-07）
    chapters.yaml        章タクソノミー
```

## パイプライン

```
leray-hopf (warm build)
    ↓ scripts/count_decls.py   [fallback]
    ↓ lake exe extract_notes   [S0 spike]
extracted/names-fallback.json  (committed)
extracted/decls.json           (S0 adds)
         ↓
corpus/**/*.yaml  ←─ 翻訳ワーカー（workpacket.py が作業パケットを生成）
         ↓
scripts/validate.py   → pass/fail
scripts/coverage.py   → site/data/coverage.json
         ↓
site/  (S2 で静的ビューア実装)
```

## クイックスタート

```bash
# 1. フックを有効化（初回のみ）
git config core.hooksPath scripts/hooks

# 2. 依存インストール
pip install pyyaml jsonschema

# 3. corpus を検証
python3 scripts/validate.py

# 4. カバレッジ確認
python3 scripts/coverage.py

# 5. 作業パケット生成（例: R3 主定理の未注釈宣言）
python3 scripts/workpacket.py --chapter capstone-r3 --lean-root /path/to/leray-hopf

# 6. 名前 universe を再生成（leray-hopf が手元にある場合）
python3 scripts/count_decls.py /path/to/leray-hopf
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
```

tier・gap の基準は `docs/schemas/corpus.schema.json` を参照。
用語は `docs/GLOSSARY.md` に準拠。

## decls.json が来たら何が変わるか

S0 スパイク完了後に `extracted/decls.json` が追加されると、以下が自動的にアップグレードされる：

- `validate.py` — decls.json の名前セットへのチェックに切り替わり、PIN も検証される
- `workpacket.py` — シグネチャ・doc コメント・依存辺が作業パケットに追加される
- `coverage.py` — より精確な chapter 分類（現在はモジュールパス heuristic）が可能になる

`names-fallback.json` はそのまま残しフォールバックとして機能し続ける。

## 参照元

- 形式化本体: `uda-lab/leray-hopf` — ローカル clone のパスを `--lean-root` に指定
- 対訳プロトタイプ: leray-hopf の `docs/formalization-review-ja.md`（GLOSSARY の種、ギャップ Note の原型）
