# 証明掘り下げインタラクティブノート UI — 全宣言対訳キャンペーン設計

## 目的

[uda-lab/lean-pde](https://github.com/uda-lab/lean-pde) の Leray–Hopf 形式化（kernel-only 達成、
80 ファイル / 42,691 LOC / **1,413 宣言**）の全定理・補題・定義に対して、Lean コードと
「自然な日本語の数学証明として読める文章」を並置した解説を与え、証明ツリーを
インタラクティブに辿れる純静的サイトを構築する。

要件（owner 指定）:

1. Lean コードの横に、対応する自然な日本語数学証明が常に読めること
2. Lean が自然言語より大幅に長くなる箇所（形式化ギャップ大）は Note として明示すること
3. インタラクティブ性: 定義はマウスオーバーで参照でき、証明中で使う Fact/Lemma は展開して掘り下げられること
4. 完全な入れ子 UI は破綻するため、深い掘り下げはリンクへ逃がし、定義群と補題群は UI 上論理的に分離すること
5. 対象は極論すべての宣言。段階的に完備化する

既存資産: lean-pde の `docs/formalization-review-ja.md`（330 行、~30–50 宣言をカバー）が
コンテンツ原型（§1–2 要所の対訳、§4 形式化ギャップ Note）。**ただし一部 stale**
（capstone 移設前の定理名を含む）— シード移植時に名前を現行ソースへ再アンカーすること。
claude.ai アーティファクト（原稿: `docs/scratch/PROJECT-SUMMARY-ARTIFACT.md`）は骨子概要であり、
本サイトとは別物として維持。

## 規模と制約（実測、コメント除去済みカウント）

| レーン | 宣言数 | うち private | 内訳 |
|---|---|---|---|
| R3 | 909 | 562 | theorem 719 / def 157 / structure 15 / instance 11 / abbrev 6 / lemma 1 |
| root（𝕋³＋共有基盤） | 435 | 173 | theorem 262 / def 90 / lemma 56 / structure 13 / instance 9 / abbrev 5 |
| Bochner | 69 | 7 | theorem 53 / def 11 / structure 4 / abbrev 1 |
| **計** | **1,413** | **742 (53%)** | theorem 1034 / def 258 / lemma 57 / structure 32 / instance 20 / abbrev 12 |

capstone: `exists_lerayHopf_r3_axiomatic`（`R3/GalerkinODECapstone.lean`）、
`exists_lerayHopf_torus3_axiomatic`（`TorusGalerkinODECapstone.lean`）。

**注釈深度ポリシー（重要）**: 宣言の 53% は private ヘルパー。
- **public 宣言（671）** = フル注釈（statement_ja＋proof_ja＋gap 判定）
- **private ヘルパー（742）** = 軽量グロス（1–3 行の役割説明）、親補題のノード配下にグループ表示。
  数学的に重い private（例: 主要補題の中核部品）はフル注釈へ随時昇格可

制約:

- lean-pde は PRIVATE。ローカルビルド環境は 3.42 GiB RAM 上限・コールドビルド禁止・
  warm .lake は main ツリーのみ。CI 自動フルビルドは廃止済み（再導入禁止）
- サイトは純静的（GitHub Pages 適合）。Pages 上限（1 GB）は本規模では非問題

## ツールチェーン判断（調査済み 2026-07-06）

- **SubVerso**（leanprover 公式、保守中）: コンパイル済みプロジェクトからハイライト済みコード＋
  **タクティク毎の証明状態**を JSON 抽出。warm build 後の抽出は軽量（再 elaboration なし）。
  → **抽出層の第一候補**。証明ステップ追跡 UI まで視野に入る
- leanblueprint: prose が LaTeX・コード表示はリンクアウトのみ・アコーディオンなし → 不採用
  （依存グラフ UI の発想のみ借用）。LeanArchitect（`@[blueprint]` 注釈→抽出、2026-06 活発）は
  依存グラフ推定の先行事例として参照
- Verso / verso-blueprint: 最有力の既製代替だが、prose を Lean ファイルとして書く強結合＋
  prose 編集毎にフル elaboration＋CJK 組版は結局手作業 → 不採用（将来の再評価は可）
- LeanInk/Alectryon: **2024-08 アーカイブ確認、死亡**。doc-gen4: フル依存閉包の doc 生成が
  重く hover 対象としては過剰 → 不採用（必要なら後から Actions manual dispatch で追加可）
- 結論: **SubVerso 抽出＋薄い自作依存グラフ抽出＋自作静的 UI**（Equational Theories /
  LeanExplore と同路線）

## アーキテクチャ(三層)

### 1. 抽出層（lean-pde 側、機械生成）

- **SubVerso** で全対象ファイルのハイライト済みコード＋証明状態 JSON を抽出（Wave 0 スパイクで
  適用可否を判定。基準: warm ツリーで RAM 3.42 GiB 内・toolchain v4.31.0-rc2 で動作）
- **薄い自作 `lake exe extract_notes`** が environment（olean ロードのみ）から補完抽出:
  完全修飾名・種別・シグネチャ pretty-print・doc-comment・ソース位置・**使用定数の依存辺**
  （proof term が参照する project 内定数 = 真の証明 DAG）・private フラグ
- 出力は本 repo の `extracted/` にコミット、対象コミット SHA を `extracted/PIN` に記録
- フォールバック（SubVerso 不適時）: 自作 exe に一本化（証明状態なし、コード表示は素の切り出し）

### 2. 注釈コーパス（本 repo、エージェント生成・レビューゲート付き）

宣言ごとに 1 YAML（`corpus/<モジュール>/<宣言名>.yaml`）:

```yaml
name: LerayHopf.R3.rellich_seq_compact   # 抽出 JSON と name でジョイン
tier: full          # full | gloss（private ヘルパーの軽量注釈）
statement_ja: |     # 主張の自然な日本語（定理文として読める文）
proof_ja: |         # 証明の日本語叙述（教科書調）；gloss 級では省略可
gap:
  level: large      # none | mild | large
  note: |           # Lean ≫ 自然言語 の箇所の解説（何が形式化で膨らむか）
chapter: compactness
tags: [rellich, frechet-kolmogorov]
```

`docs/formalization-review-ja.md` §4 のギャップ Note 文化を `gap` フィールドとして構造化する。

### 3. UI 層（本 repo、純静的）

ビルド済み JSON ＋小さな vanilla JS SPA。サーバ・ランタイムビルド不要。
1,413 ノードでもインデックス JSON 一括ロードでクライアント側検索・ホバーが成立する規模。

## UI 境界設計（入れ子問題への回答）

**展開予算の不変量: その場展開は深さ 1 まで、それ以深はナビゲーション。**

- ホバー = 定義カード（シグネチャ＋日本語 1 段落グロス）
- アコーディオン = 直接依存補題の 1 段のみその場展開（statement 対訳＋証明要約）
- さらに掘る場合は当該ノードのページへ遷移。パンくず＝capstone からの証明経路を保持
- （SubVerso 採用時）証明本文はタクティクステップ毎の証明状態トグルを提供（Alectryon 型の読書体験）
- 章立ては数学的ナラティブ（関数空間 → 射影/Galerkin → ODE → エネルギー → コンパクト性 →
  極限移行 → capstone ×2）。ノードは `#LerayHopf.R3.rellich_seq_compact` 形式の安定アンカー。
  定義群と補題群は UI 上グループ分離、private ヘルパーは親ノード配下に折り畳み
- グローバル証明 DAG ページ（capstone を根に段階的開示）＋各ノードに uses / used-by
- gap.level バッジ表示、large は Note パネル
- カバレッジダッシュボード（章別 注釈済み/全宣言、tier 別集計）

## ホスティング（確定）

- 作業場・ホスティングとも**本 repo（lean-pde-notes）**（owner 決定 2026-07-06）
- lean-pde は PRIVATE のまま。lean-pde に入る変更は抽出まわりの 1 PR のみ
- claude.ai 側 artifact 権限エージェントの作業場としても本 repo を使用
- GitHub Pages 公開の可否・時期は owner 判断で後決め（private repo の Pages はプラン依存＋
  サイトは public になる点に注意）。公開まではローカル `python -m http.server` プレビュー

## キャンペーン計画（Wave 分割、R3 先行 = owner 決定）

| Wave | 内容 | 規模 | ゲート |
|---|---|---|---|
| 0 | SubVerso スパイク＋依存辺抽出スパイク＋UI 骨格＋formalization-review-ja からシード移植（名前再アンカー込み） | シード ~30 | **go/no-go**（下記受入基準） |
| 1 | capstone 2 本＋解構造体スパイン（フル注釈） | ~50 | 主定理から辿る体験が成立 |
| 2 | R3 public 完備化（Rellich / Aubin–Lions / ODE solver / LimitPassage …） | ~350 | |
| 3 | 𝕋³＋共有基盤＋Bochner public 完備化 | ~320 | |
| 4 | private ヘルパー gloss 完備化 | ~740 | カバレッジ 100% |

**Wave 0 受入基準:**

1. 抽出 JSON の宣言数がコメント除去済み grep 集計（1,413、上表）と一致
2. 依存辺が capstone→スパインで目視妥当（`exists_lerayHopf_r3_axiomatic` の uses に
   LimitPassage 系が現れる等）
3. SubVerso＋依存辺抽出が lean-pde の warm ツリー上・RAM 3.42 GiB 内で完走（コールドビルドなし）
4. UI 骨格がローカル static サーブで動作（ホバー・1 段アコーディオン・ノード遷移・DAG 表示）
5. シード移植で stale 名の再アンカー手順が確立（旧名→現行名の対応表を残す）

**体制:** Sonnet 翻訳ワーカー（1 PR ≈ 15–30 宣言）→ Opus 数学レビュー → large-gap Note のみ
Fable。レビューゲートに wabun-math-style / math-claim-integrity 相当の検査を適用。
軽量 CI（grep 級、ビルド不要）: コーパス name 集合 ⊆ 抽出 JSON name 集合、PIN 一致検査、
YAML スキーマ検査。全 PR は本 repo で issue-first / PR-gated。

**規模見積もり:** フル注釈 671 宣言 ≈ 25–35 PR ＋ private gloss 742 宣言 ≈ バッチ 8–12 PR。
長期キャンペーンとして Wave 単位で燃焼。

## 初期化チェックリスト

- [ ] `corpus/` `extracted/` `site/` `scripts/` の骨格ディレクトリ＋スキーマ定義（YAML スキーマ、JSON スキーマ）
- [ ] lean-pde 側: 抽出（SubVerso 設定＋`extract_notes` exe）の issue 起票＋PR（本 issue を cross-ref）
- [ ] Wave 0 スパイク実施 → 受入基準判定コメントを本 issue に記録
- [ ] シード ~30 宣言の対訳移植（formalization-review-ja.md §1–2、名前再アンカー込み）
- [ ] カバレッジダッシュボード稼働（0% 表示から開始）
