# Contributing — 貢献ガイド

新規 contributor が issue 履歴を読まずに現行ワークフローを再現できることを目的とする、
最初に参照する文書。各章の詳細規約は個別ドキュメントへ誘導し、本書では重複させない。

## 1. セットアップ

`README.md` の「クイックスタート」を参照（フック有効化・依存インストール・
`validate.py` / `coverage.py` の実行）。

## 2. 注釈作業ワークフロー（annotation authoring）

1. `python3 scripts/workpacket.py --chapter <id> [--lean-root /path/to/leray-hopf]`
   で未注釈宣言の作業パケット（メタデータ + Lean ソース + YAML 雛形）を生成する。
   `--module` / `--all` / `--tier` / `--limit` などのオプションは
   `python3 scripts/workpacket.py --help` を参照。
2. 雛形を埋める。フィールドの意味・`tier` / `gap` / `proof_status` の判定基準は
   `docs/schemas/corpus.schema.json` を、執筆規約（段落・数式・レジスタ・インライン
   記法）は `corpus/README.md` を、訳語は `docs/GLOSSARY.md` を参照。
3. `python3 scripts/validate.py`（schema + corpus ⊆ universe）、
   `python3 scripts/glossary_lint.py`（訳語）、`python3 scripts/prose_lint.py`
   （組版・レジスタ、ハードエラーあり）を通す。
4. `python3 scripts/coverage.py` でカバレッジ確認、`python3 scripts/build_site_data.py`
   でサイトデータを生成し `site/` をローカルプレビューする（`site/README.md` 参照）。

## 3. 意味レビュー・チェックリスト

statement 対訳・proof_ja・gap 判定・用語集準拠の正典チェックリストは
`.github/pull_request_template.md` に置く（PR ごとに実施し埋める）。本書では複製せず、
このテンプレートを唯一の正とする。

## 4. `sorry` / scaffold / proof-status の扱い

`proof_status` フィールド（省略時 `verified`）で機械可読に管理する:
`verified` / `contains-sorry` / `scaffold` / `retired` / `invalid-statement`。
各値の意味は `docs/schemas/corpus.schema.json` の `proof_status` description を参照。
公開サイトの `#/proof-status` ルートが `verified` 以外の宣言を一覧表示する
（`site/README.md` 「Routes」節）。公理→定理化などの**歴史的経緯**は `proof_status`
にではなく任意項目 `provenance` に書く（現在の状態のみを `proof_status` は報告する）。

## 5. repin（宣言 universe 更新）手順

`leray-hopf` 側の変更に追随して `extracted/decls.json` を更新する作業。

1. `leray-hopf` のビルド済み checkout で抽出コマンドを実行し、出力をこの notes リポジトリの
   `extracted/decls.json` へ直接書き込む。相対パス `--out extracted/decls.json` は
   `leray-hopf` checkout 基準で解決されるため、notes リポジトリへの絶対パスを指定すること:
   ```bash
   NOTES_REPO=/path/to/leray-hopf-notes  # このリポジトリの絶対パス
   flock /tmp/lean-build.lock lake exe extract_notes -- --out "$NOTES_REPO/extracted/decls.json"
   ```
   その後 `extracted/PIN` を新 SHA に更新する（詳細は `extracted/README.md` 参照）。
2. `CITATION.cff` の `references[0].commit` を同じ新 SHA に更新する。`scripts/validate.py`
   は `extracted/PIN` と `CITATION.cff` の `references[0].commit` の不一致を hard fail とする
   （notes#68 のガード。`scripts/validate.py` 内の該当コメント参照）。この工程を忘れると
   次の検証で必ず失敗する。
3. `python3 scripts/decl_diff.py <旧 decls.json> extracted/decls.json --markdown <out>.md`
   で新設・削除・改名・ファイル移動を分類する。
4. corpus 側を機械的に追随する。ここでの「削除」は 2 種類を区別すること:
   - **抽出 universe から消えた宣言** — 対応する corpus YAML を削除する。`validate.py` は
     corpus ⊆ universe を強制するため、universe にない宣言の YAML を残すと検証が失敗する。
   - **universe には残るが公開経路から外れた宣言** — YAML は削除せず残し、
     `proof_status: retired` を設定する。
   改名エントリは `name:` とファイル名を追随させ、新設エントリはプレースホルダを追加する。
5. 現在進行中の repin ledger `docs/migration-2026-07-refactor.md` に、規模・分類・
   個別対応の追記節を追加する。この ledger が完全に閉じ後続に引き継がれた場合の
   archive 規約は `docs/archive/README.md` を参照。
6. `python3 scripts/validate.py` / `python3 scripts/coverage.py` で全エントリを検証する。

## 6. 生成物 / scratch / コミット対象の境界

| パス | 扱い | 由来 |
|---|---|---|
| `extracted/decls.json` | コミット済み・正典 | `lake exe extract_notes`（手順は上記 §5） |
| `extracted/names-fallback.json` | コミット済み・休眠フォールバック | `scripts/count_decls.py`（`decls.json` 欠落時のみ使用、意図的に非更新） |
| `extracted/PIN` | コミット済み | 抽出元 leray-hopf コミット SHA |
| `corpus/**/*.yaml` | コミット済み・内容をレビュー済み | 人手執筆・レビュー（§2） |
| `site/data/*.json`（`nodes.json` / `sources.json` / `coverage.json`） | **gitignored・生成物** | `scripts/build_site_data.py` / `scripts/coverage.py`。フレッシュ clone 後は存在せず、必ず自分でビルドする（`site/README.md`）。Phase A では CI が生成し workflow artifact としてのみ公開、Pages へはデプロイしない |
| `docs/` / `README.md` / `corpus/README.md` 等 | コミット済み・手動保守 | 本書のような人手ドキュメント |

## 7. 履歴文書（migration ledger）の archive 規約

`docs/` 直下の ledger には repin のたびに追記され続ける生きたものと、作業が完結し
以後更新されない閉じたものがある。閉じたものは `docs/archive/` へ移設し、警告バナーを
付す。詳細な判断基準・手順・banner フォーマットは `docs/archive/README.md` を参照。

## 8. issue / PR の書き方

- issue は `.github/ISSUE_TEMPLATE/` のテンプレートを使う。本 repo の issue は
  `## Scope` と `## Acceptance criteria` の 2 見出しを備え、優先度は `priority:P0`〜
  `priority:P3` ラベルと title の `[P0]`〜`[P3]` 接頭辞で示す規約（#63 umbrella
  参照）。
- PR は `.github/pull_request_template.md` に従う（§3 のチェックリストを含む）。

## 9. corpus batch size・レビュー分離・adversarial checks

owner 裁定（issue #75, 2026-07-19）に基づく標準方針。

### Batch size

- `tier: full` は原則 1 batch 15–25 宣言。
- `tier: gloss` は原則 1 batch 25–40 宣言。
- 数学的に重い宣言、引用を伴う宣言、複数分野をまたぐ宣言を含む場合はさらに縮小する。
- 一つの数学的 cluster として分割が不自然な場合は上限超過を許すが、PR 本文に理由と
  review 単位を明記する。

### Review separation

翻訳・文章整形と数学的意味論 review を分離する。public theorem、`sorry` / scaffold、
指数などのパラメータを持つ主張、named theorem を引用する注釈は、author とは別の
reviewer が exact Lean type と source を直接確認する。batch 全体の coverage review を、
宣言単位の数学 review の代替にしない。

### Adversarial checks

該当する場合、少なくとも次を確認する。

- 仮定・量化・結論が Lean type と一致するか。
- 端点、退化パラメータ、空集合・零元などで主張が破綻または空虚化しないか。
- 可測性、可積分性、完備性、非自明性などの暗黙の仮定を補っていないか。
- named theorem の edition / locator / hypothesis mapping が一次資料と一致するか。
- special-case の proof plan を generic claim として記述していないか。
- weighted ℓ²、spike、noncomplete、nonmeasurable 等の典型的反例が関連する場合に
  検討したか。

詳細な反例一覧は notes 側に重複して固定せず、companion source repo の
[`docs/statement-gates.md`](https://github.com/uda-lab/leray-hopf/blob/main/docs/statement-gates.md)
を canonical reference とする。
