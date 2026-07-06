## 対象宣言リスト

<!-- 追加・更新した corpus YAML のファイルパスと宣言名を列挙 -->
<!-- 例: corpus/LerayHopf/R3/AxiomaticClosure/exists_lerayHopf_r3_axiomatic.yaml -->

- [ ] 

## tier 内訳

| tier | 件数 |
|------|------|
| full | |
| gloss | |

## gap 判定サマリ

| gap level | 件数 |
|-----------|------|
| none | |
| mild | |
| large | |

large gap がある場合、`gap.note` に形式化膨張の理由を記載済みであること。

## GLOSSARY 追記有無

- [ ] 新語なし（既存の GLOSSARY で対応済み）
- [ ] 新語あり → `docs/GLOSSARY.md` に追記済み（行数: ）

## 数学レビューチェックリスト

**statement_ja 対訳チェック**
- [ ] statement_ja の主張が Lean の定理文と一致する（量化子・仮定・結論が漏れなく対応）
- [ ] 数学用語が GLOSSARY の確立訳語に準拠している
- [ ] 略語・記号の初出で説明を添えた
- [ ] 数式・記法は KaTeX 記法（インライン `$...$` / ディスプレイ `$$...$$`）で書き、
      ブロックスカラー（`| 記法`）に収めた（`corpus/README.md`「数式記法」節を参照）

**組版・レジスタチェック（notes#12 v1.1 — `scripts/prose_lint.py`）**
- [ ] D1: prose フィールドは 1 段落 = 1 物理行、段落区切りは空行（段落内で折り返さない）
- [ ] D2: 長い／重い数式はディスプレイ `$$...$$`、数式内に Lean 宣言名を書いていない
- [ ] D3: `statement_ja` / `proof_ja` は数学書の文体のみ（Lean 用語・tactic 名なし）。
      Lean 固有の注意は `gap.note` に置いた
- [ ] D5: インライン記法は `` `code` `` / `**強調**` / `[[表示語|宣言名]]` と KaTeX のみ。
      `[[…]]` の参照先は実在する宣言名
- [ ] `python3 scripts/prose_lint.py` がハードエラーなし

**proof_ja チェック（tier: full + theorem/lemma の場合）**
- [ ] proof_ja が実際の証明経路と一致する（Lean の主要タクティクステップを反映）
- [ ] ステップ番号（L1, L2, …）または見出しがあり追跡可能
- [ ] 自然言語では暗黙の前提（tsum 規約、代表元選択など）を NOTE として明記した

**gap 判定チェック**
- [ ] gap.level の判定根拠が明確（none: ほぼ同じ / mild: 細部補足要 / large: 大幅膨張）
- [ ] large の場合 gap.note に具体的な膨張箇所を記載した

**用語集準拠**
- [ ] `python3 scripts/glossary_lint.py` が警告なし（または警告を確認・対処済み）

## CI 確認

- [ ] `python3 scripts/validate.py` 通過
- [ ] `python3 scripts/prose_lint.py` 通過（ハードエラーなし）
- [ ] `npm test`（jsdom レンダーハーネス）通過
- [ ] GitHub Actions ワークフロー (`harness.yml`) グリーン
