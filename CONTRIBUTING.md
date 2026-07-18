# Contributing — 貢献ガイド

新規 contributor が issue 履歴を読まずに現行ワークフローを再現できることを目的とする
一次入口。各章の詳細規約は個別ドキュメントへ誘導し、本書では重複させない。

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

1. warm な `leray-hopf` checkout で
   `flock /tmp/lean-build.lock lake exe extract_notes -- --out extracted/decls.json`
   を実行し、`extracted/PIN` を新 SHA に更新する（`extracted/README.md` 参照）。
2. `python3 scripts/decl_diff.py <旧 decls.json> extracted/decls.json --markdown <out>.md`
   で新設・削除・改名・ファイル移動を分類する。
3. corpus 側を機械的に追随（改名・削除エントリの retire・新設エントリのプレースホルダ
   追加など）。
4. 現在進行中の repin ledger `docs/migration-2026-07-refactor.md` に、規模・分類・
   個別対応の追記節を追加する。この ledger が完全に閉じ後続に引き継がれた場合の
   archive 規約は `docs/archive/README.md` を参照。
5. `python3 scripts/validate.py` / `python3 scripts/coverage.py` で全行検証する。

## 6. 生成物 / scratch / コミット対象の境界

| パス | 扱い | 由来 |
|---|---|---|
| `extracted/decls.json` | コミット済み・正典 | `lake exe extract_notes`（手順は上記 §5） |
| `extracted/names-fallback.json` | コミット済み・休眠フォールバック | `scripts/count_decls.py`（`decls.json` 欠落時のみ使用、意図的に非更新） |
| `extracted/PIN` | コミット済み | 抽出元 leray-hopf コミット SHA |
| `corpus/**/*.yaml` | コミット済み・source-reviewed | 人手執筆・レビュー（§2） |
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

## 9. 未整備の項目

以下は #75 の "Suggested content" に挙がっているが、既存の確立された運用がないため
本書では新規に規定していない。owner 裁定を経てから追加する:

- corpus batch size（1 バッチあたりの宣言数）の目安と、数学レビューを翻訳作業から
  分離する運用のポリシー化。
- adversarial boundary-case / counterexample チェックリスト（§3 の数学レビュー
  チェックリストへの追加項目として検討）。
