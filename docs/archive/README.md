# docs/archive/

Fully-closed historical records — kept for provenance, no longer appended to and no
longer authoritative for current state.

## いつ archive するか

`docs/` には repin・移行のたびに追記される **生きた ledger**（例:
`docs/migration-2026-07-refactor.md`）と、ある一時点で作業が完結し以後更新されない
**閉じた記録**の二種類がある。後者だけをここに置く。目安:

- その ledger が対象とする移行・repin が完了し、後継の ledger（多くは同種の生きた
  ledger の追記節）に引き継がれている。
- 内容が現行の正典ではなく、「なぜこの corpus entry が存在するか」のような来歴説明
  としてのみ有用。

生きた ledger を書きかけのまま archive しないこと。まだ追記され得るなら `docs/` 直下
に残す。

## 手順

1. `git mv docs/<name>.md docs/archive/<name>.md` — ファイル名は変更しない。
2. 冒頭に警告バナーを追加/確認する（下記フォーマット）。既存の
   `docs/archive/seed-migration-mapping.md` を参考にする。
3. 他ドキュメント・スクリプトからのパス参照を更新する（`grep -rn '<old-path>'`）。
   `scripts/check_docs.py` の `EXEMPT_DOCS` のような明示的パスリストは特に見落としやすい。

## banner フォーマット

閉じた記録であることが本文冒頭で分かるように、以下を満たす引用ブロックを置く:

- 何時点のスナップショットか（PIN / 日付など）。
- 現行の正典が何か（通常 `extracted/decls.json` + `extracted/PIN`、または後継の生きた
  ledger）への具体的なポインタ。
- この記録が今なお有用な理由（来歴・provenance としてのみ、等）。

## 現在のエントリ

- `seed-migration-mapping.md` — S3 シード移植時（PIN `013c4a0`）の旧名→現行名対応表。
  移植作業完結後は追記されていない。
