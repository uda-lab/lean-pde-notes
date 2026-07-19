# 2026-07 リファクタリング波 追随 — 宣言 universe 移行記録（PIN 013c4a0 → a33de86）

`uda-lab/lean-pde` の pre-publication リファクタリング波（issue #108/#110/#111/#112/#113/#114/#131
= PR #116–#138、2026-07-09〜07-11）に伴う corpus・宣言マッピングの追随記録。
PR ごとの宣言レベル差分の全履歴は notes#36 のコメント群に集約されている。本書はその
corpus 側への適用結果（何をどう機械的に変更したか）を記録する。

対応は新 PIN `a33de86522a13d05d7cee67fbc27b1b9106822f8` 時点の `extracted/decls.json`
（正典の名前 universe）で全行検証済み。

本書は repin のたびに追記される生きた ledger であり、追記が止まり後続に引き継がれた
時点で `docs/archive/`（規約は `docs/archive/README.md` 参照）へ移す。

## 規模

| | 旧（013c4a0） | 新（a33de86） |
|---|---|---|
| 抽出宣言数 | 1,412 | 1,347 |
| corpus エントリ数 | 1,412 | 1,137（本波の機械的追随後） |
| display-name 衝突 | 7 組 14 宣言 | 2 組 4 宣言（`measurable_natFloor_real`, `continuous_restrictToBall'`） |

分類（`scripts/decl_diff.py` による）: 新設 +213（public 78 / private 135）、削除 −278
（public 13 / private 265）、ファイル移動 467（名前不変 — #116 の Torus/ 移設と #111/#113/#114
のファイル分割・抽出）、private→public 昇格 58、public→private 降格 0。

再現手順:

```bash
git show <旧コミット>:extracted/decls.json > /tmp/decls-old.json
python3 scripts/decl_diff.py /tmp/decls-old.json extracted/decls.json --markdown /tmp/diff.md
```

## 名称が変わったもの（エントリ改名、3 件 — lean-pde PR #117）

| 旧名 | 現行名 | 備考 |
|---|---|---|
| `LerayHopf.exists_lerayHopf_r3_axiomatic` | `LerayHopf.exists_lerayHopf_r3` | ℝ³ capstone。`_axiomatic` 接尾辞の retire |
| `LerayHopf.exists_lerayHopf_torus3_axiomatic` | `LerayHopf.exists_lerayHopf_torus3` | 𝕋³ capstone。同上 |
| `LerayHopf.exists_lerayHopf_torus3_statement` | `LerayHopf.Scaffold.exists_lerayHopf_torus3_statement` | scaffold placeholder の namespace 隔離 |

corpus 側: YAML の `name:`・ファイル名を改名し、`[[…\|旧名]]` ホバー参照を全 corpus で
再ターゲットした。

## 削除された public 宣言（13 件）とその後継

| 削除された宣言 | 後継 / 対応 |
|---|---|
| `exists_lerayHopf_r3_axiomatic` ほか rename 3 件 | 上表の改名（削除ではない） |
| `GalerkinCompactnessPackage`（GalerkinPackage.lean ごと削除） | `LerayHopf.Galerkin.CompactnessPackage`（PR #134） |
| `exists_lerayHopf_from_galerkin_package`（ExistenceFromPackage.lean ごと削除） | `LerayHopf.Galerkin.exists_lerayHopf_from_package`（PR #134） |
| `galerkinODE_bilinearPart` / `galerkinODE_linearPart`（両 lane、計 4 件） | 汎用層 `LerayHopf.Galerkin.bilinearPart` / `linearPart`（private、PR #132–#133） |
| `eLpNorm_three_le_interp_pub` | `LerayHopf.PlancherelKernels.eLpNorm_three_le_interp`（PR #121） |
| `memH1_weightedL2_integrable` | 孤児化した Bessel 系の削除（PR #126）。実用途は `memH1_weightedL2_integrable_R` |
| `Bochner.GelfandTriple.ιCLM` | 死んだ互換 shim の削除（PR #127）。後継なし |
| `TorusConvectionExtension.summable_coeff_sq'` | 共有化で `Torus.summable_norm_mFourierCoeff3_sq` 等へ集約（PR #124） |

## 削除された private 宣言（265 件）

#111 dedup 波（Fresh copy・CLM tower・restrictToBall 族などの逐語コピー）、#112 の lane 側
ODE body、#131 の TraceEnergy Hilbert toolkit 重複が主。個別の後継は notes#36 の各 PR
コメントに記録済み。corpus 側は対応する 265 エントリ（ほぼ全て `generated` gloss）+
display-name 衝突解消で不要になった重複エントリを retire した（計 275 YAML 削除）。

## ホバー参照の個別修正（5 件）

| 参照元 | 旧ターゲット | 新ターゲット |
|---|---|---|
| `convIntegralSchwartz_add_1` | `LerayHopf.convForm`（旧 universe でも dangling だった既存不良参照） | `LerayHopf.convIntegralSchwartz` |
| `convIntegralSchwartz_bound_energy` | `eLpNorm_three_le_interp_pub` | `PlancherelKernels.eLpNorm_three_le_interp` |
| `galerkinODE_vectorField_contDiff` | `galerkinODE_bilinearPart` / `galerkinODE_linearPart` | `Galerkin.bilinearPart` / `Galerkin.linearPart` |
| `integrable_viscous_integrand_of_memH1` | `memH1_weightedL2_integrable` | `memH1_weightedL2_integrable_R` |

## 新設宣言（+213）と注釈フォローアップ

新章 `galerkin-generic` を追加（`docs/schemas/chapters.yaml` 末尾）。未注釈の新設宣言は
本移行 PR の時点では coverage 未達として残り、後続の注釈パケット（notes#36 参照）で
埋める:

- **Galerkin 汎用層**（PR #132/#134、新章 galerkin-generic）: `Galerkin/DissipativeODE.lean`
  公開 6、`Galerkin/QuadraticField.lean` 公開 8（`FieldForms` ほか）、`Galerkin/Domain.lean`
  公開 3（`Domain`, `NSFormCore`, `Domain.evolution`）、`Galerkin/SolutionBundles.lean` 公開 4
  （`SolutionData`, `LerayHopfSolution`, `CompactnessPackage`, `exists_lerayHopf_from_package`）
- **lane witness / instance**（PR #133/#134）: `torusDomain` / `r3Domain` + 簡約補題 8、
  `Torus3NSForms.core` / `R3NSForms.core` + `core_b`、`torusFieldForms` / `r3FieldForms`、
  `galerkinODE_vectorField_eq_generic`（両 lane）
- **共有解析モジュール**（PR #120–#127）: `Analysis/TensorEdgeGluing` 公開 10、
  `Analysis/BoundedMultiplier` 公開 11、`Analysis/PlancherelKernels` 公開 8、
  `Analysis/BilinearExtension` 公開 3
- **b(u,v,v)=0 系**（PR #128）: `DissipativeEvolution.convForm_self_zero_right`,
  `Torus3NSForms.b_self_zero_right`, `R3NSForms.b_self_zero_right`
- **#114 教科書ステップ補題**（PR #129/#130）: TraceEnergy 6・WeakLeibniz 2 ほか —
  抽出上は private（新設 private 135 に含まれる）。注釈単位として設計されており、
  数学的に重いものは 2 層ポリシーの昇格条項で full 化してよい
- **private→public 昇格 58 件**（PR #121–#130）: FourierParseval 14、SpatialCompactness 13、
  RealComplexLpBridge 10、GalerkinODEExistence 7 ほか。public=full の 2 層ポリシーにより
  gloss→full 格上げ対象

## 適用しなかったもの

- `extracted/names-fallback.json` は設計通り休眠のまま非更新（`extracted/README.md` 参照）。
- `origin/corpus/annotation-upgrade` ブランチ（seed 2 エントリ）は、その内容が既に main の
  `AbstractEnergyLaw.energyInequality.yaml` / `Bochner.ContDiffBump.isTimeMollifier.yaml` に
  取り込まれていることを確認済み — 完全に superseded であり、取り込み不要（ブランチは削除可）。

## 将来の変動要因

`uda-lab/lean-pde#135`（ArzelaAscoliTime / GoodRepresentative の GalerkinDomain
インターフェースへの restate — stretch、時期未定）。実施された場合は本書と同じ手順
（`decl_diff.py` → 機械的追随 → 注釈フォローアップ）を小規模に繰り返す。

→ 実施された。次節（PIN a33de86 → 0afd65f）を参照。

## 追記: 小規模 repin（PIN a33de86 → 0afd65f、notes#60）

lean-pde PR #139/#141/#142/#143（issue #135 の restate〔縮小スコープ〕と issue #1
finding-6 の成分往復補題の共有化、docs 整理 2 件）への追随。抽出宣言数 1,347 → 1,349、corpus エントリ数 1,347 → 1,349（全宣言 coverage 維持）。

`decl_diff.py` による分類と corpus 側対応:

| 区分 | 宣言 | corpus 側対応 |
|---|---|---|
| private→public 昇格（H1Sigma.lean → Torus/DivergenceFree.lean へ移動、成分往復補題の共有化） | `re_compLpL_projComponentC`, `sum_inject_projComponent` | 2 層ポリシー（public=full）により gloss→full 格上げ。旧抽出元ファイルへの言及を更新 |
| 新設 private | `injectComponent_projComponent_ae`（Torus/DivergenceFree.lean）, `galerkin_norm_le_u0_generic`（R3/GoodRepresentative.lean） | gloss エントリ新設 |
| 署名変更（issue #135 restate: 仮定の Galerkin 解束を `GalerkinSolutionData_R3` から汎用束 `Galerkin.SolutionData (r3Domain 𝔊) F.core` へ一般化。主張の内容は不変） | `galerkin_weakLimit_R3`, `perTest_lipschitz_R3`, `perTest_hasDerivAt_R3` | full 2 件は gap.note に束の一般化を追記。gloss 1 件（`perTest_hasDerivAt_R3`）は本文影響なし |
| 削除 | なし | — |

display-name 衝突は 2 組 4 宣言（`measurable_natFloor_real`, `continuous_restrictToBall'`）のまま不変。
`extracted/names-fallback.json` は引き続き休眠・非更新。


## 追記 2: release-blocker 波 repin（PIN 0afd65f → d5f91f7、lean-pde#145 P0/P1）

lean-pde の公開前 P0/P1 波（issue #144/#146/#147/#148/#149/#150/#153/#158/#166/#168
= PR #159–#165/#167/#169、2026-07-16 夜〜07-17 未明）への追随。抽出宣言数 1,349 → 1,339、
corpus エントリ数 1,349 → 1,339（全宣言 coverage 維持）。

| 区分 | 宣言 | corpus 側対応 |
|---|---|---|
| 削除 −10（#144: 空虚な scaffold API と被参照ゼロ定義の除去） | `SpatialField`, `LerayHopfSolution`（旧 placeholder 版）, `ExistsLerayHopf`, `Scaffold.exists_lerayHopf_torus3_statement`, `LerayHopfNonunique`, `H1Torus`, `lerayProjection`, `lerayProjection_R3`, `AbstractGalerkinData`, `convFormSchwartzWitness` | エントリ retire（10 YAML 削除） |
| 移動+署名変更（#147/#158: Experimental 分離と偽一般形の修正） | `Bochner.w1pTime_continuous_in_H`（TimeSobolev.lean → TimeSobolevExperimental.lean、`1 ≤ p,q` → `p=q=2`） | エントリを issue #158 に従い検疫記述へ更新（一般形は偽・反例・制限と隔離の経緯を gap.note に記録） |

注: root import は #147 で sorry-free 化され、sorry 入り Bochner 4 モジュールは
`LerayHopf.Experimental` 経由でのみ到達可能となった。notes の抽出 universe は
owner 裁定（2026-07-17）により root + Experimental の両方をカバーする
（lean-pde#166 で extractor を拡張、本 repin から適用）。

## 追記 3: release candidate freeze repin（PIN d5f91f7 → 7c15710a、leray-hopf-notes#32 Phase B）

owner 裁定（issue #32、2026-07-19T15:49:25Z）による source release candidate 凍結
（`uda-lab/leray-hopf@7c15710a7b9068a2aa105fc7c11b432e7685b7b5`）への追随。leray-hopf
#151/#152/#154/#155/#156/#157/#158/#173/#177/#178/#180（PR #170–#183 の範囲、docstring/private
境界の triage・maxHeartbeats 注釈・Temam/Sobolev 記法修正・rename sync・release-cone guard 強化）
を含む 23 commits。

`lake exe extract_notes` 再実行（フレッシュビルド、実際にコンパイルされたのは 9 モジュールの
み・残り 3187 ジョブはキャッシュ再利用）: 抽出宣言数 1,339 → 1,339（増減なし）。
`decl_diff.py` による分類:

| 区分 | 件数 | 内容 | corpus 側対応 |
|---|---|---|---|
| 追加/削除/移動 | 0 | — | — |
| public→private 可視性変更（issue #155 の docstring/private 境界 triage） | 24 | すべて `LerayHopf/Torus/ConvectionExtension.lean` 内（`convBLTw` 系・`l2coeff` 系など） | 本 repin では機械的差分のみ反映（PIN/CITATION.cff 更新）。2 層ポリシー（public=full）に従うと該当 24 件は tier: full → gloss への格下げ対象だが、gloss 文面の手書き作業は本 PR のスコープ外 — 別 issue でフォローアップ |
| signature text 変更（同上 triage の副作用、doc-only） | 13 | 上記 24 件のサブセット | 同上（tier 格下げと合わせてフォローアップ） |

display-name 衝突は 2 組 4 宣言のまま不変。`validate.py` / `coverage.py` はともに green
（1339/1339 coverage、tier 不整合は非致命 — `validate.py` は `tier ∈ {full, gloss}` のみ検査
し public/private との整合は検査対象外）。`extracted/names-fallback.json` は引き続き休眠・
非更新。
