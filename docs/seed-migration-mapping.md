# S3 シード移植 — 旧名→現行名 対応表（formalization-review-ja → コーパス）

> **⚠ 履歴記録（PIN `013c4a0` 時点）** — この対応表は移植作業当時の一時点のスナップショットで
> あり、現行の指示・現行の宣言名を保証するものではない。以後の repin（`docs/migration-2026-07-refactor.md`
> 等を参照）で宣言名が再度変わっている場合がある。例えば下表「現行名」列の
> `exists_lerayHopf_torus3_axiomatic` / `exists_lerayHopf_r3_axiomatic` は本記録作成後の
> repin で `_axiomatic` 接尾辞が retire され、現在は `LerayHopf.exists_lerayHopf_torus3` /
> `LerayHopf.exists_lerayHopf_r3` である。**宣言名の正典は常に `extracted/decls.json`
> （現在の PIN は `extracted/PIN` を参照）** であり、本表は「なぜこの corpus entry が
> 存在するか」という来歴の記録として読むこと。

`uda-lab/lean-pde` の対訳プロトタイプ `docs/formalization-review-ja.md` を新スキーマの
コーパス YAML へ移植した際の、宣言名の再アンカー記録。対応先は PIN `013c4a0` 時点の
`extracted/decls.json`（正典の名前 universe）で検証済み。

## 最重要の陳腐化（doc §5 の前提が古い）

レビュー文書 §5 は「**T³ は 4 公理、ℝ³ は 6 公理**で閉じる」と述べるが、これは執筆当時の状態。
その後の公理除去キャンペーンにより、**プロジェクトは現在 kernel-only（公理ゼロ）に到達**している
（`extracted/decls.json` に `kind: axiom` の宣言は 0 件、`#print axioms` は
`propext / Classical.choice / Quot.sound` のみ）。§5 が「公理」として挙げる宣言はすべて、
証明済み定理へ置換されたか、gap 構造体へ再編されている。各コーパス entry の `gap.note` は
この現行状態（Lean 側の実態）を優先して記述し、doc の公理フレーミングは採らない。

## 名称が変わったもの（再アンカー）

| doc の名称 | 現行名（decls.json） | kind | 備考 |
|---|---|---|---|
| `exists_lerayHopf_torus3` | `LerayHopf.exists_lerayHopf_torus3_axiomatic` | theorem | `_axiomatic` は歴史的接尾辞。本体はカーネルのみ |
| `exists_lerayHopf_r3` | `LerayHopf.exists_lerayHopf_r3_axiomatic` | theorem | 同上 |
| `P_N`（§2.1 の射影） | `LerayHopf.fourierProjection_n` | def | スカラー Fourier 截断射影 |

## 名称が同じもの（そのまま移植）— entry を作成した宣言

`DissipativeEvolution` / `WeakFormNS` / `DissipativeEvolution.convForm_self_zero` /
`AbstractEnergyLaw` / `L2Sigma` / `divSymbol` / `L2Sigma_R3` / `divTestFunctional` /
`h1EnergySq` / `viscousFormSq` / `viscousFormSq_R3` / `stokesTestPairing_R3` /
`memH1VF_R3` / `velocityProjection_n` / `fourierProjection_n` / `lerayProjection` /
`lerayProjection_R3` / `mFourierCoeff3` / `convIntegralSchwartz` / `galerkinConvection` /
`IsSchwartzDivFree_R3` / `rellich_seq_compact` / `H1_ball_totallyBounded` /
`L2C_norm_sq_eq_tsum_coeff_sq` / `fourierProjection_n_mFourierCoeff` / `H1_tail_bound` /
`H1_ball_uniform_L2_approx` / `rellich_L2Sigma` / `abstract_galerkin_energy_identity` /
`velocityProjection_n_component_comm` / `conjL2C_fourierProjection` /
`LerayHopfSolutionFull` / `LerayHopfSolutionFull_R3`（すべて `LerayHopf.` 名前空間）。

`AubinLionsPackage` / `AubinLionsPackage_R3` は doc §5 の Aubin–Lions 公理に対応する
現行の構造体で、entry を作成（旧公理 `aubin_lions` / `aubin_lions_R3` は証明済み定理
`torusAubinLionsPackage_of_galSeq` / `aubinLionsPackage_R3_of_timeCompactness` へ置換済み）。

## doc §5 の宣言で、独立 entry を作らなかったもの（意図的に保留）

以下は doc が「公理」として解説する宣言だが、現在はいずれも**大きな証明済み定理**へ
置換・再編されている。tier:full の定理 entry は `proof_ja` に「Lean が実際に行う証明」を
書く必要があり、それには各巨大証明の精読が要る（シード移植の範囲外）。そのため独立 entry は
作らず、数学的内容と「公理→定理」の履歴は関連する def/structure entry の `gap.note`
（`galerkinConvection` / `convIntegralSchwartz` / `AubinLionsPackage(_R3)` / `IsSchwartzDivFree_R3`）
および 2 つの capstone entry の `gap.note` に集約した。

| doc の名称（公理として解説） | 現行の対応 | kind | 保留理由 |
|---|---|---|---|
| `torus3_NSForms_exist` | `torus3_NSForms_exists` → `torusConvectionGap_exists` へ再編 | theorem | 大きな証明済み定理。内容は `galerkinConvection` の gap.note で言及 |
| `r3_NSForms_exist` | `r3_NSForms_exists` → `r3ConvectionGapOp_exists` へ再編 | theorem | 同上。内容は `convIntegralSchwartz` の gap.note |
| `galerkin_ode_solution` (T³) | 除去。`galerkinSolutionData_torus` + `Torus.galerkinODE_*` へ | — | capstone `exists_lerayHopf_torus3_axiomatic` の proof_ja/gap.note に集約 |
| `galerkin_ode_solution_R3` | 除去。`galerkinSolutionData_unconditional` + `schemeOfBasis` へ | — | capstone `exists_lerayHopf_r3_axiomatic` に集約 |
| `galerkin_limit_passage` (T³) | `torus_galerkin_limit_passage_of_energyClass` | theorem | 大きな証明済み定理 |
| `galerkin_limit_passage_R3` | `galerkin_limit_passage_R3`（公理→定理、2026-07-05 除去） | theorem | 同上 |
| `r3GalerkinScheme_exists` | `r3GalerkinScheme_exists`（公理→定理） | theorem | 証明済み。capstone は意図的にこれを迂回（基底を捨てないため） |
| `spatial_compactness_R3` | `spatial_compactness_R3`（公理→定理） | theorem | 局所 Rellich。内容は `AubinLionsPackage_R3` の gap.note |

## 移植件数

37 entry（`tier: full`）を作成。章別内訳：spaces 13 / projections-galerkin 5 / energy 5 /
compactness 8 / limit-passage 2 / capstone-r3 2 / capstone-torus 2。既存の 3 サンプル
（`exists_lerayHopf_r3_axiomatic` / `rellich_seq_compact` / `L2Sigma_R3`）はいずれも
シード集合と重なるため、実内容へアップグレードし `sample` タグを除去した。
