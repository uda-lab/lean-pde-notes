# 2026-07-14 日本語校正監査 所見台帳

- **一次資料**: issue [#51](https://github.com/uda-lab/lean-pde-notes/issues/51) のコメント 1–2（`FINDING | file | field | rule | severity | 逐語引用 | 問題 | 書き換え案` 形式、全 371 件）。
- **安定 ID**: コメント掲載順に F001–F371（コメント 1/2 → 2/2 の順、SUMMARY 行は除外）。
- **status**: `open`（未処理）／ `fixed`（修正済み、処理 PR を note に記載）／ `rejected`（却下、理由を note に記載）／ `superseded-by-#52`（#50 の用語裁定 PR #52 で処理済み）。
- 台帳生成時（2026-07-15）に逐語引用と現行 corpus の突き合わせを機械実施し、#52 処理済み項目を `superseded-by-#52` に初期化した。引用列は識別用の先頭 32 字（正規化前の原文は issue コメント参照）。
- **2026-07-15 再検証**（PR #53 owner レビュー指摘）: `superseded-by-#52` 全件について「引用消失＝完了」ではなく**所見の問題自体が解消されているか**を個別確認した。同一引用範囲への別修正で引用が消えていた 8 件（F035/F040/F211/F214/F249/F261/F274/F279）を `open` に戻した。F096 は reopen 後 P1 で即時修正。

| ID | file | field | rule | sev | chapter | status | note |
|---|---|---|---|---|---|---|---|
| F001 | AbstractGalerkinData | proof_ja | 表記(D3) | M | energy | fixed | P1: proof_ja: removed インスタンス/フィールド, reworded as 実内積の構造/一括りのデータ. Combined with F072 on same span. |
| F002 | EnergyData | proof_ja | 表記(D3) | M | energy | fixed | P1: proof_ja: フィールドとして束ねる → 一組のデータとして指定する. Combined with F073. |
| F003 | torus_galerkin_norm_le_u0 | proof_ja | 表記(D3) | M | energy | fixed | P1: proof_ja: エネルギー有界フィールドから → エネルギー有界性から. Combined with F084 (same span, both files identical quote). |
| F004 | viscousEnn | gap.note(表示語) | 自然さ | M | energy | superseded-by-#52 |  |
| F005 | Torus.galerkinField_inner_self_nonpos | proof_ja | JP-13/自然さ | M | ode | fixed | P1: proof_ja: 委譲する→帰着する. Combined with F089 (内実は→具体的には). Also applied the same 委譲→帰着 fix to the other decls this finding named (energy_hasDerivAt_of_localSolution, galerkinField_solution_agree, galerkinField_uniform_local_time, norm_le_of_forwardSolution). |
| F006 | Torus.galerkinODE_vectorField_contDiff | gap.note | 造語 | B | ode | fixed | P1: gap.note: 有効化補題 → Picard–Lindelöf 定理に必要な滑らかさを与える補題. Combined with F095 (same span). |
| F007 | summable_norm_mFourierCoeff3_sq | gap.note | JP-13 | M | ode | fixed | P1: gap.note: ODE 機構なしで → ODE に関する結果へ依存せずに. Combined with F108 (same span). |
| F008 | Torus.energy_hasDerivAt_of_localSolution | proof_ja | 自然さ | M | ode | fixed | P1: proof_ja: 微分の往復 → 内在的微分と周囲空間の微分の相互の読み替え. |
| F009 | Torus.galerkinField_solution_agree | gap.note | 自然さ | M | ode | fixed | P1: gap.note: 継ぎ足して→接続して (both occurrences in the paragraph fixed for coherence). decls.json checked: LerayHopf.Torus.galerkinField_solution_agree doc = 'splice-agreement: two local solutions agreeing at one point agree on the overlap' — 貼り合わせ/接続 preserve this exactly. |
| F010 | L2VF_norm_sq_eq_sum_componentC | proof_ja/gap.note | 表記(訳語ゆれ) | M | ode | fixed | P1: 殆ど至る所 (proof_ja) and a.e. (gap.note) both unified to ほとんど至る所. |
| F011 | exists_galerkin_modewise_extraction | proof_ja | JP-13/造語 | B | compactness | fixed | P1: 証人+帯域水準→截断次数の複合書き換え（F130 と統合適用） |
| F012 | exists_galerkin_modewise_extraction | proof_ja | JP-13 | B | compactness | open | 一様部分列抽出の汎用エンジン |
| F013 | exists_limit_curve_of_galSeq | proof_ja | JP-13 | B | compactness | open | 配線の定理である |
| F014 | exists_limit_curve_of_galSeq | proof_ja | 自然さ/JP-13 | M | compactness | open | のエクスポートを添えて |
| F015 | exists_limit_curve_of_galSeq | gap.note | JP-13 | M | compactness | open | が握る唯一の取っ手となる capstone |
| F016 | galerkin_u_norm_le | statement_ja | 自然さ | M | compactness | open | 一様球有界（エクスポート形） |
| F017 | integral_tail_sq_limit_le | gap.note | JP-13 | M | compactness | open | 極限曲線に密輸しない誠実な経路 |
| F018 | galerkin_test_pairing_lipschitz | statement_ja | 造語/自然さ | A | compactness | fixed | P1: 帯域水準→截断次数（owner 裁定 2026-07-15b、statement_ja + gap.note の 2 箇所） |
| F019 | tail_sq_le_h1EnergySq_div | statement_ja | 造語/自然さ | M | compactness | open | 尾部の $H^1$ 優越 |
| F020 | DivFreeL2 | statement_ja | 自然さ | M | spaces | fixed | P1: statement_ja: 「発散ゼロ性の」→「発散がゼロであることの」. decls.json checked: doc confirms 'Fourier characterisation of div u=0 for L2 vector fields'; meaning preserved. |
| F021 | DivFreeL2 | gap.note | JP-14 | M | spaces | superseded-by-#52 |  |
| F022 | L2VF | gap.note | JP-13 | A | spaces | fixed | P1: gap.note theater metaphor 「主舞台」→「中心」(same span as F110, one edit serves both). |
| F023 | IsGalerkinTest | gap.note | JP-14 | M | capstone-torus | superseded-by-#52 |  |
| F024 | IsGalerkinTest | gap.note | 造語 | M | capstone-torus | open | Faedo–Galerkin の標準テスト級 |
| F025 | torus3Evolution | statement_ja | 造語 | M | capstone-torus | open | テスト級は [[Galerkin テスト\|LerayHopf.I |
| F026 | torus3Evolution | gap.note | JP-14 | M | capstone-torus | superseded-by-#52 |  |
| F027 | ExistsLerayHopf | statement_ja | 自然さ/表記 | M | misc | open | 最初期スキャフォールド |
| F028 | LerayHopfNonunique | gap.note | JP-14/自然さ | M | misc | open | Branch B（非一意性方面） |
| F029 | lower_bound_from_inverse_square_lifespan | gap.note | JP-14 | M | misc | open | Branch 探索期の独立補題 |
| F030 | mem_velocitySpan_of_fixed | proof_ja | JP-13/借用語彙 | B | projections-galerkin | fixed | P1: 自身を原像として取る形に書き換え（F206 と統合適用） |
| F031 | velocityP_initial_mem | proof_ja | JP-13/借用語彙 | B | projections-galerkin | fixed | P1: u0 自身を取る形に書き換え（F208 と統合適用） |
| F032 | fourierCoeffCLM_apply | gap.note | JP-13/比喩 | M | projections-galerkin | open | Fourier 係数を「連続線形汎関数の値」と見なす視点の切り替 |
| F033 | velocityProjection_n_inner_of_fixed | statement_ja | 自然さ | M | projections-galerkin | open | 帯域制限テストとの対は截断を素通しする |
| F034 | fourierCoeffCLM | statement_ja | 造語/自然さ | M | projections-galerkin | open | 第 $k$ Fourier 係数の連続線形汎関数化 |
| F035 | velocitySpan | gap.note | JP-13/表記 | M | projections-galerkin | open | 再検証で reopen: lane→系列 は #52 処理済みだが「鏡像」が残存 |
| F036 | fourierProjection_n_tendsto | gap.note | 表記/訳語ゆれ | M | projections-galerkin | superseded-by-#52 |  |
| F037 | mem_velocitySpan_iff | gap.note | JP-14/表記 | M | projections-galerkin | open | 以下の bridge 補題群（固定点と像の一致）の出発点。 |
| F038 | fourierBox_exhausts | statement_ja | 自然さ | A | projections-galerkin | superseded-by-#52 |  |
| F039 | exists_uniform_subseq_of_lipschitz_family | statement_ja | JP-13/造語 | B | bochner | open | 一様収束部分列（対角線論法エンジン） |
| F040 | exists_uniform_subseq_of_lipschitz_family | statement_ja | JP-14 | M | bochner | fixed | P1: eventually→ある番号以降で（reopen 後、owner 裁定に従い修正） |
| F041 | exists_uniform_subseq_of_lipschitz_family | gap.note | 造語 | M | bochner | fixed | P1: 載荷点→技術上の要点（owner 裁定 2026-07-15b）+ 同文の帯域水準→截断次数 |
| F042 | exists_Icc_of_compact_subset_Ioo | gap.note | JP-13 | M | bochner | open | 同時に収める区間を取る簿記の補題 |
| F043 | isWeakTimeDeriv_zero_ae_const | statement_ja | JP-13 | M | bochner | open | du Bois-Reymond の要石： |
| F044 | w1pTime_continuous_in_H | proof_ja | JP-13 | M | bochner | open | 良い代表元理論の柱に当たる |
| F045 | timeConvL2_weakDeriv_comm | gap.note | JP-13 | M | bochner | open | 時間軟化理論の心臓部 |
| F046 | w1pTime_lineExtension | proof_ja | JP-13 | M | bochner | open | 糊の部品 — 切断の Leibniz 積則 |
| F047 | translationModulus_zero | gap.note | 造語 | M | bochner | open | 連続性論法の錨点 |
| F048 | timeMollification_exists | proof_ja | JP-13/自然さ | M | bochner | open | 区間 $[0, T]$ への移送が壁である |
| F049 | hToVprimeCLM | proof_ja | JP-13/自然さ | M | bochner | open | その双対への正直な連続線形写像 |
| F050 | isWeakTimeDerivℝ_smul_cutoff | proof_ja | 自然さ | M | bochner | open | コンパクト台（$\psi$ の台が勝つ） |
| F051 | isWeakTimeDerivℝ_smul_cutoff | gap.note | 自然さ | M | bochner | open | Bochner 積分がジャンク値になり得る |
| F052 | GelfandTriple | gap.note | 自然さ | M | bochner | open | primal 側だけ持てば冗長がない |
| F053 | GelfandTriple | statement_ja | JP-14 | M | bochner | open | の primal データ：実 Hilbert |
| F054 | GelfandTriple | gap.note | JP-14 | M | bochner | open | は載せない（No-overclaim）。 |
| F055 | aeStronglyMeasurable_of_spaceTimeL2 | gap.note | JP-14 | M | bochner | open | 仮定に隔離している（no-smuggle：仮定は |
| F056 | IsOfDissipativeEvolution | statement_ja | JP-13/造語 | M | bochner | open | 忠実性契約：Gelfand 三つ組が |
| F057 | isWeakTimeDeriv_comp_clm | statement_ja | 造語/自然さ | M | bochner | open | 弱時間微分の連続線形写像による輸送 |
| F058 | continuous_translationModulus | statement_ja | 表記(訳語ゆれ) | A | bochner | open | 並進モジュラスの連続性 |
| F059 | convBLTgalerkin | proof_ja | JP-13 | B | limit-passage | fixed | P1: 証人比喩を除去（F316 と統合適用） |
| F060 | convValW | statement_ja | 造語 | B | limit-passage | superseded-by-#52 |  |
| F061 | convBLTw | statement_ja/proof_ja | 造語 | M | limit-passage | superseded-by-#52 |  |
| F062 | TorusConvectionExtension.convFormL2_antisymm | gap.note | JP-13 | M | limit-passage | open | 監査記載パスは corpus/LerayHopf/convFormL2_antisymm.yaml（同名の双子ファイル）; 実所在 corpus/LerayHopf/TorusConvectionExtension.convFormL2_antisymm.yaml |
| F063 | convSummandW | gap.note | JP-13 | M | limit-passage | superseded-by-#52 |  |
| F064 | TorusConvectionExtension.detExtend | gap.note | JP-13 | M | limit-passage | open | 監査記載パスは corpus/LerayHopf/detExtend.yaml（同名の双子ファイル）; 実所在 corpus/LerayHopf/TorusConvectionExtension.detExtend.yaml |
| F065 | convValW_bound | gap.note | JP-13 | M | limit-passage | open | 極限移行の心臓部 |
| F066 | convValW_eq_convFormFourier | gap.note | JP-13 | M | limit-passage | open | 相殺機構 |
| F067 | galerkinConvection_antisymm | gap.note | JP-13 | M | limit-passage | open | 相殺機構は同じ |
| F068 | velocityProjection_n_eq_of_le | gap.note | JP-13 | M | limit-passage | open | ODE を発火させる |
| F069 | convFormL2_galerkin_pin | statement_ja | JP-14 | M | limit-passage | superseded-by-#52 |  |
| F070 | convFormL2_def | gap.note | JP-14 | A | limit-passage | superseded-by-#52 |  |
| F071 | AbstractGalerkinData | statement_ja | 造語 | B | energy | rejected | 却下: issue #51 G2 裁定「束／データ束」は変更不要（owner レビュー指摘により statement_ja を原文へ復元。proof_ja の Lean 語修正は F001 で維持） |
| F072 | AbstractGalerkinData | proof_ja | 表記 | B | energy | fixed | P1: proof_ja: rewritten to remove インスタンス/フィールド, kept 束ねた (bundling, not Lean jargon). See F001. |
| F073 | EnergyData | proof_ja | 表記 | B | energy | fixed | P1: proof_ja: フィールド removed. decls.json checked: LerayHopf.EnergyData doc = 'kinetic energy E, accumulated dissipation A, viscosity ν' — the three-quantity content is unchanged, only 'フィールドとして束ねる' reworded. |
| F074 | EnergyData | gap.note | JP-13 | M | energy | fixed | P1: gap.note: 抽象スケルトン層 → 抽象化段階. |
| F075 | EnergySkeleton.EnergyInequality | gap.note | JP-13 | M | energy | fixed | P1: gap.note: 抽象層 → で導入された抽象的な定義. |
| F076 | H1SigmaTorus | gap.note | 自然さ | M | energy | superseded-by-#52 |  |
| F077 | convFormFourier | gap.note | 自然さ | M | energy | fixed | P1: gap.note: 真正な値を持つ領域 → 意味のある値を与える領域. |
| F078 | convFormFourier_antisymm_galerkinTest | proof_ja | JP-13 | B | energy | fixed | P1: proof_ja: 一本に合流し → 一つの総和にまとめることができ (adapted rewrite to keep 合流後 consistent, changed to まとめた後). |
| F079 | convFormFourier_antisymm_galerkinTest | gap.note | JP-13 | M | energy | fixed | P1: gap.note: 持ち回りの管理 → 各段階での確認. |
| F080 | convSummand | statement_ja | 自然さ | M | energy | fixed | P1: statement_ja grammar fix: 足し実部を取ると → 足して実部を取ると. No technical-term/meaning change, no decls.json check needed (particle-only fix). |
| F081 | memH1VF_zero | proof_ja | 自然さ | M | energy | fixed | P1: proof_ja: 零、したがって → 零であり、したがって. |
| F082 | ofReal_viscousFormSq_le | proof_ja | 表記 | B | energy | fixed | P1: proof_ja: ジャンク値規約により$0$に潰れる → 総和可能でない場合の実数値の総和は定義上$0$となる. decls.json checked: LerayHopf.ofReal_viscousFormSq_le doc = 'the junk-0 collapse only helps the inequality' — matches; meaning preserved. |
| F083 | torus_galerkin_energy_le | gap.note | JP-16 | M | energy | superseded-by-#52 |  |
| F084 | torus_galerkin_norm_le_u0 | proof_ja | 表記 | B | energy | fixed | P1: same edit as F003. |
| F085 | torus_galerkin_norm_le_u0 | gap.note | 自然さ | M | energy | superseded-by-#52 |  |
| F086 | viscousEnn | gap.note | JP-13 | M | energy | fixed | P1: 「正直な和」→「発散時には∞を返す総和」のみ適用。同文の橋渡しは G2 裁定により維持 |
| F087 | L2VF_norm_sq_eq_sum_componentC | proof_ja | 自然さ | M | ode | fixed | P1: proof_ja: Euclid ノルム二乗 → ユークリッドノルムの二乗. |
| F088 | Torus.energy_hasDerivAt_of_localSolution | proof_ja | 自然さ | M | ode | fixed | P1: proof_ja: 内実は → 具体的には. Combined with F008/F005 edits on same paragraph. |
| F089 | Torus.galerkinField_inner_self_nonpos | proof_ja | 自然さ | M | ode | fixed | P1: same edit as F005. |
| F090 | Torus.galerkinField_solution_agree | statement_ja | 自然さ | B | ode | fixed | P1: statement_ja: 継ぎ足しの整合性 → 貼り合わせの整合性. decls.json checked, same verdict as F009 (splice-agreement on overlap) — meaning preserved. |
| F091 | Torus.galerkinField_uniform_local_time | proof_ja | 自然さ | M | ode | fixed | P1: proof_ja: 内実は Picard–Lindelöf の局所存在 → 具体的には Picard–Lindelöf の局所存在定理を用いる. Also fixed 委譲する→帰着する in same sentence per F005's scope. |
| F092 | Torus.galerkinField_uniform_local_time | gap.note | 自然さ | M | ode | fixed | P1: gap.note: 継ぎ足して → 順次貼り合わせて (both occurrences in paragraph updated for coherence). |
| F093 | Torus.galerkinODE_functional | statement_ja | JP-16 | B | ode | superseded-by-#52 |  |
| F094 | Torus.galerkinODE_vectorField_contDiff | proof_ja | 自然さ | M | ode | fixed | P1: proof_ja: 汎用側の内実は → 汎用定理では. |
| F095 | Torus.galerkinODE_vectorField_contDiff | gap.note | 造語 | B | ode | fixed | P1: same edit as F006. |
| F096 | Torus.galerkinODE_vectorField_contDiff | gap.note | 造語 | B | ode | fixed | P1: 「系列ごと の…段積み構成」→「系列ごとに構成していた…段階的な合成」（再検証での reopen を即時修正） |
| F097 | Torus.galerkinODE_vectorField_spec | statement_ja | JP-13 | B | ode | rejected | 却下: issue #51 G2 裁定「橋渡し」は変更不要（和語として定着）— 監査書き換え案を適用せず原文維持 |
| F098 | Torus.norm_le_of_forwardSolution | proof_ja | 自然さ | M | ode | fixed | P1: proof_ja: 微分の往復 → 部分空間内での微分と全空間での微分を対応させる. Also fixed 委譲する→帰着する per F005's scope. |
| F099 | stokesTestPairing_add_left | statement_ja | JP-16 | B | ode | superseded-by-#52 |  |
| F100 | stokesTestPairing_add_right | statement_ja | JP-16 | B | ode | superseded-by-#52 |  |
| F101 | stokesTestPairing_add_right | proof_ja | JP-13 | B | ode | fixed | P1: proof_ja: 一本に合流でき → 総和可能な族の和として一つにまとめられ. |
| F102 | stokesTestPairing_diag | statement_ja | JP-16 | B | ode | superseded-by-#52 |  |
| F103 | stokesTestPairing_diag | gap.note | JP-13 | M | ode | fixed | P1: gap.note: 粘性散逸へ落ちる → 粘性散逸に等しいことを用いる (restructured surrounding clause for grammaticality). |
| F104 | stokesTestPairing_smul_left | statement_ja | JP-16 | B | ode | superseded-by-#52 |  |
| F105 | stokesTestPairing_smul_right | statement_ja | JP-16 | B | ode | superseded-by-#52 |  |
| F106 | stokesTestPairing_smul_right | proof_ja | 表記 | B | ode | fixed | P1: proof_ja: mathlib では無条件に成立する → removed, restated as plain mathematical fact (実スカラー倍は総和と交換できるので従う). decls.json checked: LerayHopf.Torus.stokesTestPairing_smul_right doc = 'Right-homogeneity of stokesTestPairing on Vₙ' — no mathlib-specific content lost, scalar-summation commutativity is a general fact independent of the mathlib remark. |
| F107 | stokesTestPairing_symm | statement_ja | JP-16 | B | ode | superseded-by-#52 |  |
| F108 | summable_norm_mFourierCoeff3_sq | gap.note | JP-13 | M | ode | fixed | P1: 機構→ODE に関する結果へ依存せず（重複所見と統合適用） |
| F109 | DivFreeL2 | gap.note | 自然さ | M | spaces | superseded-by-#52 |  |
| F110 | L2VF | gap.note | JP-13 | M | spaces | fixed | P1: Same span as F022; applied 「本形式化の中心となる Hilbert 空間」(chose over the alternate ADVISORY suggestion since it stays closer to original meaning than 「主に用いる」). |
| F111 | SpatialField | statement_ja | JP-13 | B | spaces | fixed | P1: statement_ja: 「場所取りの型」→「暫定的に導入された型」, kept 領域 Ω and 空間場 context that the suggested rewrite had dropped. decls.json checked: doc = 'Placeholder for a spatial field on a domain Ω... Realized as a real function space in a later milestone' — meaning preserved (still a contentless placeholder). |
| F112 | SpatialField | proof_ja | 表記 | B | spaces | fixed | P1: proof_ja: removed Lean 'フィールド' jargon, applied suggested rewrite verbatim: 「台となる型と恒真命題だけからなる形式的な定義である。」decls.json checked: structure signature Type u_1 → Type (u_2+1) is consistent with a carrier-type field plus a trivial proposition; meaning preserved. |
| F113 | SpatialField | gap.note | JP-13 | M | spaces | fixed | P1: gap.note 「最初期マイルストーン（M1）の足場で」→「最初期のマイルストーン（M1）で導入され」, combined with F114 in one coherent sentence. |
| F114 | SpatialField | gap.note | 自然さ | M | spaces | fixed | P1: gap.note 「歴史的残置物である」→「現在は使用されていない旧定義である」, applied together with F113. |
| F115 | Time | gap.note | 造語 | B | spaces | fixed | P1: gap.note 「時間変数の意図を型面で明示する」→「時間変数であることを型によって明示する」, applied suggested rewrite verbatim. |
| F116 | Torus3 | statement_ja | 自然さ | M | spaces | fixed | P1: statement_ja: 「三つ組の直積」→「$3$ 重直積」(matched existing $N$ 個/次元 math notation style in the file). decls.json checked: doc = 'realized as UnitAddTorus (Fin 3) = Fin 3 → UnitAddCircle', a 3-fold product; meaning preserved. |
| F117 | VelocityValue | statement_ja | 自然さ | B | spaces | fixed | P1: statement_ja: 「Euclid 内積とノルムを込めて」→「標準内積とそれに付随するノルムを備えた」. Kept 'Euclid' (not 'ユークリッド') per corpus-wide established convention (grepped: Domain3.yaml, L2VF_R3_separable.yaml, PlancherelKernels*.yaml all use 'Euclid 空間/ノルム' consistently) — using the suggested rewrite's 'ユークリッド' would have violated JP-14 (undeclared language alias) and GLOSSARY consistency. decls.json checked: doc = 'EuclideanSpace ℝ (Fin 3)' with standard inner product; meaning preserved. |
| F118 | exists_galerkin_test_family | proof_ja | JP-13 | B | spaces | fixed | P1: proof_ja: 「一本の N 添字の列に平坦化する」→「自然数で添字付けられた一つの列として番号付けする」, applied suggested rewrite verbatim. |
| F119 | exists_galerkin_test_family | proof_ja | 表記 | B | spaces | fixed | P1: proof_ja: 「生成系のリストの範囲外は零で埋める」→「各有限生成系を番号付けし、その番号の範囲外では零を対応させる」, applied together with F118 in the same sentence; kept mathlib-specific Nat.pair/unpair detail in gap.note (no finding there). |
| F120 | h1EnergySq_nonneg | statement_ja | 自然さ | B | spaces | superseded-by-#52 |  |
| F121 | h1EnergySq_nonneg | proof_ja | 自然さ | M | spaces | superseded-by-#52 |  |
| F122 | memH1Torus | gap.note | JP-13 | M | spaces | fixed | P1: gap.note 「定義に採用した足場である」→「定義として採用したものである」, applied suggested rewrite verbatim. |
| F123 | stokesTestPairing_bound_of_galerkinTest | statement_ja | JP-16 | B | spaces | superseded-by-#52 |  |
| F124 | torus3_mFourierBasis | proof_ja | 表記 | B | spaces | fixed | P1: proof_ja: removed 'mathlib の多次元加法トーラスの' library reference, rewrote as 「一般の加法トーラスの Fourier Hilbert 基底の理論を 3 次元の場合に特殊化し、三次元トーラスの標準 Fourier 基底として指数関数系を得る」, preserving the '特殊化' term since gap.note cross-references 'この特殊化'. Moved the mathlib-specific detail (`UnitAddTorus.mFourierBasis`, d = Fin 3) into gap.note per D3. decls.json checked: doc confirms 'This is UnitAddTorus.mFourierBasis instantiated at d = Fin 3'; meaning preserved. |
| F125 | torus3_mFourierBasis | gap.note | JP-13 | M | spaces | fixed | P1: gap.note 「この基底の Hilbert 基底性から流れ出す」→「この基底が Hilbert 基底であることから従う」, applied together with F124's gap.note addition. |
| F126 | viscousFormSq_nonneg | statement_ja | 自然さ | B | spaces | superseded-by-#52 |  |
| F127 | instIsProbabilityMeasureUnitAddCircleVolume_lerayHopf | proof_ja | 表記 | B | spaces | fixed | P1: proof_ja: removed 'mathlib の...インスタンスの形に包み直すだけである' Lean-implementation phrasing, rewrote as 「既知の等式「単位加法円周の全測度は 1」から、標準測度が確率測度であることが従う。」gap.note already covers the instance-declaration detail appropriately. |
| F128 | volume_torus3_eq_haarTorus3 | proof_ja | 自然さ | M | spaces | fixed | P1: proof_ja: 「積測度の構成関数の合同で 3 因子に持ち上げる」→「各因子の測度が一致することから 3 重積測度も一致する」, applied suggested rewrite verbatim. |
| F129 | L2C_norm_sub_fourierProjection_sq | proof_ja | 表記 | B | compactness | open | 補集合上の部分型の総和 |
| F130 | exists_galerkin_modewise_extraction | proof_ja | JP-13 | B | compactness | fixed | P1: F011 と統合適用 |
| F131 | exists_galerkin_modewise_extraction | proof_ja | JP-13 | B | compactness | open | 一様部分列抽出の汎用エンジン |
| F132 | exists_galerkin_modewise_extraction | proof_ja | 表記 | B | compactness | open | `exists_uniform_subseq_of_lipsch |
| F133 | exists_limit_curve_of_galSeq | proof_ja | JP-13 | B | compactness | open | 配線の定理である |
| F134 | exists_limit_curve_of_galSeq | proof_ja | JP-13 | B | compactness | open | のエクスポートを添えて |
| F135 | exists_limit_curve_of_galSeq | gap.note | JP-13 | M | compactness | open | 唯一の取っ手となる capstone |
| F136 | exists_weak_limit_curve | statement_ja | 自然さ | B | compactness | superseded-by-#52 |  |
| F137 | exists_weak_limit_curve | proof_ja | JP-14 | M | compactness | superseded-by-#52 |  |
| F138 | exists_weak_limit_curve | proof_ja | 造語 | B | compactness | superseded-by-#52 |  |
| F139 | galerkin_test_pairing_lipschitz | statement_ja | 造語 | B | compactness | open | 帯域水準 $m$ のテスト $w$ |
| F140 | galerkin_test_pairing_lipschitz | proof_ja | 表記 | B | compactness | open | ODE フィールドで書き下す |
| F141 | galerkin_test_pairing_lipschitz | proof_ja | 造語 | B | compactness | open | および一様球有界 |
| F142 | galerkin_test_pairing_lipschitz | gap.note | JP-13 | M | compactness | open | ODE フィールドが発火する |
| F143 | galerkin_u_continuousOn | proof_ja | 表記 | B | compactness | open | 前向き微分可能性フィールドにより |
| F144 | galerkin_u_norm_le | statement_ja | 造語 | B | compactness | open | 一様球有界（エクスポート形） |
| F145 | galerkin_u_norm_le | proof_ja | 表記 | B | compactness | open | エネルギー有界フィールド |
| F146 | h1EnergySq_continuousOn_galerkin | proof_ja | JP-13 | B | compactness | open | 有限和に潰れる |
| F147 | integral_sq_proj_tendsto_zero_of_weak | statement_ja | 造語 | B | compactness | open | 各時刻の弱収束と一様球有界 |
| F148 | integral_sq_proj_tendsto_zero_of_weak | proof_ja | 造語 | B | compactness | open | 各座標は弱対そのもの |
| F149 | integral_tail_sq_galerkin_le | proof_ja | 表記 | B | compactness | open | 解データの $H^1$ 正則性フィールド |
| F150 | integral_tail_sq_limit_le | proof_ja | JP-13 | B | compactness | open | Galerkin 側の実数経路は使えない |
| F151 | integral_tail_sq_limit_le | proof_ja | 造語 | B | compactness | open | ENNReal 橋渡し |
| F152 | integral_tail_sq_limit_le | gap.note | JP-13 | M | compactness | open | $H^1$ 所属を極限曲線に密輸しない |
| F153 | ofReal_tail_sq_eq_tailEnn | statement_ja | 造語 | B | compactness | open | 尾部の拡張非負実数橋渡し |
| F154 | ofReal_tail_sq_eq_tailEnn | proof_ja | 自然さ | M | compactness | open | で実側を書き換え |
| F155 | tailEnn_lsc_of_weak | proof_ja | 造語 | B | compactness | open | 積添字（成分と箱外格子点の対） |
| F156 | tailEnn_lsc_of_weak | gap.note | JP-13 | M | compactness | open | Fatou 型の骨組み |
| F157 | tail_sq_le_h1EnergySq_div | proof_ja | 表記 | B | compactness | open | 補題 `H1_tail_bound` に委譲 |
| F158 | tail_sq_le_h1EnergySq_div | gap.note | JP-13 | M | compactness | open | tsum のジャンク $0$ 潰れ |
| F159 | tendsto_inner_L2VF_of_tendsto_inner_L2Sigma | statement_ja | 造語 | B | compactness | open | 弱収束のテスト級の昇格 |
| F160 | tendsto_inner_L2VF_of_tendsto_inner_L2Sigma | gap.note | JP-13 | M | compactness | open | 到達可能にする接続部品 |
| F161 | GalerkinCompactnessPackageFull | statement_ja | JP-16 | B | capstone-torus | open | エネルギークラス所属 |
| F162 | GalerkinCompactnessPackageFull | proof_ja | 造語 | B | capstone-torus | open | 形式束の中核 |
| F163 | GalerkinCompactnessPackageFull | gap.note | JP-16 | M | capstone-torus | open | Leray–Hopf エネルギークラスに属する |
| F164 | IsGalerkinTest | gap.note | 造語 | B | capstone-torus | open | Faedo–Galerkin の標準テスト級 |
| F165 | IsGalerkinTest | gap.note | 自然さ | M | capstone-torus | superseded-by-#52 |  |
| F166 | build_galerkin_package_of_galSeq | proof_ja | 表記 | B | capstone-torus | open | Rellich 埋め込み `rellich_L2Sigma` |
| F167 | build_galerkin_package_of_galSeq | proof_ja | JP-16 | M | capstone-torus | open | エネルギークラス仮定を |
| F168 | build_galerkin_package_of_galSeq | proof_ja | JP-13 | B | capstone-torus | open | 証明保持構造に詰める |
| F169 | build_galerkin_package_of_galSeq | gap.note | 表記 | M | capstone-torus | open | import 循環回避のため |
| F170 | build_galerkin_package_of_torus | proof_ja | JP-13 | B | capstone-torus | open | 組み立ての中核に渡すだけである |
| F171 | exists_lerayHopf_from_package_full | proof_ja | 表記 | B | capstone-torus | open | 各証明フィールドが解構造の各フィールドへ |
| F172 | galSeq_of_torus | proof_ja | 表記 | B | capstone-torus | open | `galerkinSolutionData_torus`）を呼ぶ |
| F173 | stokesTestPairing | gap.note | JP-16 | M | capstone-torus | open | tsum のジャンク値規約 |
| F174 | stokesTestPairing | gap.note | 自然さ | M | capstone-torus | open | 真正な値を持つ領域の管理 |
| F175 | torus3Evolution | statement_ja | 造語 | B | capstone-torus | open | トーラスの散逸発展の束 |
| F176 | torus3Evolution | proof_ja | 造語 | B | capstone-torus | open | 形式束の中核を渡す |
| F177 | torus3Evolution | gap.note | 造語 | B | capstone-torus | open | Galerkin テスト級でテストする |
| F178 | torus3Evolution | gap.note | 自然さ | M | capstone-torus | superseded-by-#52 |  |
| F179 | ExistsLerayHopf | statement_ja | JP-13 | B | misc | open | 最初期スキャフォールド |
| F180 | ExistsLerayHopf | proof_ja | 表記 | B | misc | open | `LerayHopfSolution`（`Statement.l |
| F181 | ExistsLerayHopf | gap.note | JP-13 | M | misc | open | 歴史的スキャフォールドとして残る |
| F182 | LerayHopfNonunique | statement_ja | JP-13 | B | misc | open | スキャフォールドのみ |
| F183 | LerayHopfNonunique | gap.note | JP-13 | M | misc | open | Branch B（非一意性方面）の目標文の場所取り |
| F184 | exists_lerayHopf_torus3_statement | statement_ja | 表記 | B | misc | open | 歴史的な目標文（意図的な sorry） |
| F185 | exists_lerayHopf_torus3_statement | proof_ja | 表記 | B | misc | open | 証明は意図的に `sorry` のまま残されている |
| F186 | exists_lerayHopf_torus3_statement | proof_ja | JP-13 | B | misc | open | この定理を「閉じる」ことは不誠実 |
| F187 | lower_bound_from_inverse_square_lifespan | gap.note | 自然さ | M | misc | open | 爆発レート下界の初等的な言い換え（Branch 探索期 |
| F188 | L2VF_ext_componentC_mFourierCoeff | proof_ja | 自然さ | M | projections-galerkin | open | 実側へ落ちる |
| F189 | componentC_mem_fourierSpan | gap.note | JP-13 | M | projections-galerkin | open | スカラー側から引き出す接続部品 |
| F190 | divFreeL2_iff_divSymbol | gap.note | JP-13 | M | projections-galerkin | open | 記述を往復させる橋 |
| F191 | fourierBox_exhausts | statement_ja | JP-17 | B | projections-galerkin | superseded-by-#52 |  |
| F192 | fourierCoeffCLM | statement_ja | 造語 | B | projections-galerkin | open | 第 $k$ Fourier 係数の連続線形汎関数化 |
| F193 | fourierCoeffCLM | proof_ja | 造語 | B | projections-galerkin | open | 内積の連続線形汎関数化 |
| F194 | fourierCoeffCLM_apply | gap.note | JP-13 | M | projections-galerkin | open | 視点の切り替え弁 |
| F195 | fourierProjection_n_tendsto | proof_ja | 表記 | B | projections-galerkin | open | という mathlib の一般定理に |
| F196 | fourierSpan_hasOrthogonalProjection | proof_ja | JP-13 | B | projections-galerkin | open | 一般インスタンスが自動で発火する |
| F197 | fourierSpan_iSup_dense | proof_ja | JP-17 | B | projections-galerkin | superseded-by-#52 |  |
| F198 | instHasOrthogonalProjectionRealSubtypeAEEqFunTorus3VelocityValueHaarTorus3MemAddSubgroupL2VFL2Sigma | statement_ja | 表記 | B | projections-galerkin | open | Leray 射影の存在の型クラス化 |
| F199 | instHasOrthogonalProjectionRealSubtypeAEEqFunTorus3VelocityValueHaarTorus3MemAddSubgroupL2VFL2Sigma | proof_ja | JP-13 | B | projections-galerkin | open | 一般インスタンスが完備性の登録から自動で発火する |
| F200 | isClosed_L2Sigma | gap.note | JP-13 | M | projections-galerkin | open | 直接の配当である |
| F201 | lerayProjection_isSymmetric | gap.note | 造語 | B | projections-galerkin | open | 弱収束のテスト級の昇格 |
| F202 | mem_sigma_of_mem_velocitySpan | statement_ja | 造語 | B | projections-galerkin | open | $V_n$ の元の発散ゼロ所属（部分型の形の言い換え） |
| F203 | mem_sigma_of_mem_velocitySpan | proof_ja | 表記 | B | projections-galerkin | open | 包含を部分型の元に適用するだけ |
| F204 | mem_velocitySpan_iff | gap.note | 自然さ | M | projections-galerkin | open | 以下の bridge 補題群 |
| F205 | mem_velocitySpan_of_fixed | statement_ja | 自然さ | B | projections-galerkin | open | 固定点は像に属する（bridge の逆方向） |
| F206 | mem_velocitySpan_of_fixed | proof_ja | JP-13 | B | projections-galerkin | fixed | P1: F030 と統合適用 |
| F207 | velocityP_fixes_span | statement_ja | 自然さ | B | projections-galerkin | open | 像は固定される（bridge の片方向） |
| F208 | velocityP_initial_mem | proof_ja | JP-13 | B | projections-galerkin | fixed | P1: F031 と統合適用 |
| F209 | velocityProjection_n_comp_of_le | statement_ja | JP-13 | B | projections-galerkin | open | 小さい箱への截断は大きい箱を忘れる |
| F210 | velocityProjection_n_inner_of_fixed | statement_ja | JP-13 | B | projections-galerkin | open | 帯域制限テストとの対は截断を素通しする |
| F211 | velocitySpan | gap.note | 自然さ | M | projections-galerkin | open | 再検証で reopen: 「鏡像」残存（F035 と同件） |
| F212 | velocitySpanToSigma | statement_ja | 表記 | B | projections-galerkin | open | 発散ゼロ所属の証明とともに発散ゼロ空間の元として包み直す |
| F213 | velocitySpanToSigma | proof_ja | JP-17 | B | projections-galerkin | open | 台の元は変えず、所属証明を |
| F214 | velocitySpanToSigma | gap.note | JP-13 | M | projections-galerkin | open | 再検証で reopen: lane→系列 は #52 処理済みだが「型の橋」が残存 |
| F215 | velocitySpanToSigma_add | proof_ja | 表記 | B | projections-galerkin | open | 部分型の外延性で一致する |
| F216 | velocitySpanToSigma_coe | statement_ja | JP-17 | B | projections-galerkin | open | 埋め込みの台の値の保存 |
| F217 | velocitySpanToSigma_coe | proof_ja | 表記 | B | projections-galerkin | open | 定義的等式（`rfl`）である |
| F218 | velocitySpanToSigma_smul | proof_ja | 表記 | B | projections-galerkin | open | 部分型の外延性で従う |
| F219 | velocitySpan_hasOrthogonalProjection | proof_ja | JP-13 | B | projections-galerkin | open | 一般インスタンスが自動で発火する |
| F220 | velocitySpan_le_sigma | gap.note | JP-13 | M | projections-galerkin | open | 定義した配当 |
| F221 | Bochner.ContDiffBump.isTimeMollifier | proof_ja | 自然さ | B | bochner | open | フィールドごとに充てるだけである。 |
| F222 | Bochner.ContDiffBump.isTimeMollifier | gap.note | JP-13 | M | bochner | open | 軟化子の具体的な供給源。半径を潰す列を取れば |
| F223 | Bochner.IsTimeMollifier | proof_ja | 自然さ | B | bochner | open | 四条件をフィールドとして束ねた述語構造である。 |
| F224 | Bochner.WeakLimitToolkit.cauchySeq_inner_extend | proof_ja | 造語 | B | bochner | open | 一様球有界 |
| F225 | Bochner.WeakLimitToolkit.cauchySeq_of_equiLipschitz_of_dense | statement_ja | 造語 | B | bochner | fixed | P1: #52（等→同程度 Lipschitz）+ P1（「連続（性）」付与、owner 裁定）で解消 |
| F226 | Bochner.WeakLimitToolkit.cauchySeq_of_equiLipschitz_of_dense | proof_ja | 造語 | B | bochner | fixed | P1: #52（等→同程度 Lipschitz）+ P1（「連続（性）」付与、owner 裁定）で解消 |
| F227 | Bochner.WeakLimitToolkit.exists_mem_of_ae_full | statement_ja | 自然さ | M | bochner | open | a.e. に成り立つ集合 $S$ |
| F228 | Bochner.WeakLimitToolkit.exists_weak_limit_in_submodule | statement_ja | 自然さ | M | bochner | open | すべてのテスト $z$ に対し対の列が Cauchy |
| F229 | Bochner.WeakLimitToolkit.exists_weak_limit_in_submodule | proof_ja | 造語 | B | bochner | open | 球有界から $M$ 有界性が従う |
| F230 | GelfandTriple | statement_ja | JP-14 | B | bochner | open | の primal データ |
| F231 | GelfandTriple | proof_ja | 自然さ | B | bochner | open | 二つの Hilbert 空間の構造（型とインスタンス） |
| F232 | IsOfDissipativeEvolution | statement_ja | 造語 | B | bochner | open | 忠実性契約 |
| F233 | IsOfDissipativeEvolution | proof_ja | 自然さ | B | bochner | open | 型の等しさとインスタンスの異型等式 |
| F234 | IsWeakTimeDeriv | proof_ja | 造語 | B | bochner | open | （全導関数込みで）消える |
| F235 | IsWeakTimeDerivℝ | gap.note | 造語 | B | bochner | open | Fubini 障害 |
| F236 | TimeMollification | statement_ja | 自然さ | B | bochner | open | をフィールドとして束ねる。 |
| F237 | TimeMollification | proof_ja | 自然さ | B | bochner | open | 六つのフィールド |
| F238 | W1pTime | statement_ja | 自然さ | B | bochner | open | フィールドは、$V'$ 値の微分曲線 |
| F239 | W1pTime | proof_ja | 自然さ | B | bochner | open | フィールドに持つ構造として定める。 |
| F240 | aeStronglyMeasurable_of_spaceTimeL2 | proof_ja | JP-13 | B | bochner | open | 二段の一般論を直列に適用する。 |
| F241 | aeStronglyMeasurable_of_spaceTimeL2 | gap.note | JP-13 | M | bochner | open | 可測性は別口で供給されるべき欠けた柱 |
| F242 | continuousOn_primitive_of_integrableOn | statement_ja | 自然さ | M | bochner | open | 上区間可積分な曲線 |
| F243 | continuous_translationModulus | statement_ja | 造語 | B | bochner | open | 並進モジュラス |
| F244 | dist_toLp_stepCurve | gap.note | JP-13 | M | bochner | open | 形式へ戻す橋。 |
| F245 | exists_Icc_of_compact_subset_Ioo | statement_ja | JP-17 | B | bochner | open | 閉区間による分離 |
| F246 | exists_Icc_of_compact_subset_Ioo | gap.note | JP-13 | M | bochner | open | 簿記の補題。 |
| F247 | exists_subseq_tendsto_eLpNorm_of_totallyBounded | gap.note | JP-13 | M | bochner | open | A1–A6 の鎖の出口。 |
| F248 | exists_uniform_subseq_of_lipschitz_family | statement_ja | JP-13 | B | bochner | open | 対角線論法エンジン |
| F249 | exists_uniform_subseq_of_lipschitz_family | statement_ja | JP-14 | B | bochner | fixed | P1: F040 と統合適用 |
| F250 | exists_uniform_subseq_of_lipschitz_family | statement_ja | 造語 | B | bochner | fixed | P1: #52（等→同程度 Lipschitz）+ P1（「連続（性）」付与、owner 裁定）で解消 |
| F251 | exists_uniform_subseq_of_lipschitz_family | proof_ja | 造語 | B | bochner | open | 一様 Cauchy 化 |
| F252 | exists_uniform_subseq_of_lipschitz_family | gap.note | 造語 | B | bochner | fixed | P1: F041 と統合適用 |
| F253 | exists_unitMass_weight | gap.note | JP-13 | M | bochner | open | 要石で「a.e. 定数の値」を汲み出す |
| F254 | hToVprimeCLM | statement_ja | 自然さ | B | bochner | open | 束ねられた連続線形写像として構成する。 |
| F255 | hToVprimeCLM | proof_ja | JP-13 | B | bochner | open | 正直な連続線形写像 |
| F256 | hToVprimeCLM_apply | statement_ja | 自然さ | B | bochner | open | CLM 版と裸の埋め込み |
| F257 | integrable_timeMollifier_smul_translate | gap.note | JP-14 | M | bochner | open | side condition なしで |
| F258 | isCompact_stepCurve_toLp | proof_ja | 造語 | B | bochner | open | 値リストから類への組み立て写像 |
| F259 | isWeakTimeDeriv_primitive | statement_ja | JP-14 | B | bochner | open | 分布的 FTC |
| F260 | isWeakTimeDeriv_primitive | proof_ja | 自然さ | M | bochner | open | `sorry`（ALLOW_SORRY）で開けてある。 |
| F261 | isWeakTimeDeriv_primitive | gap.note | JP-14 | M | bochner | open | 再検証で reopen: lane→系列 は #52 処理済みだがソフトウェア的「閉じている」が残存 |
| F262 | isWeakTimeDeriv_unique | gap.note | JP-14 | M | bochner | open | body コメント |
| F263 | isWeakTimeDeriv_zero_ae_const | statement_ja | JP-13 | B | bochner | open | du Bois-Reymond の要石 |
| F264 | isWeakTimeDerivℝ_comp_clm | proof_ja | JP-13 | B | bochner | open | 全直線への移植 |
| F265 | isWeakTimeDerivℝ_smul_cutoff | proof_ja | JP-13 | B | bochner | open | $\psi$ の台が勝つ |
| F266 | isWeakTimeDerivℝ_smul_cutoff | gap.note | JP-13 | M | bochner | open | Bochner 積分がジャンク値になり得る |
| F267 | ofDissipativeEvolution | statement_ja | 造語 | B | bochner | open | 忠実性契約 |
| F268 | ofDissipativeEvolution | proof_ja | 自然さ | B | bochner | open | フィールドに詰めて |
| F269 | ofHValuedDeriv | gap.note | JP-14 | M | bochner | open | primal 定義 |
| F270 | primitive_baseA_props | statement_ja | 自然さ | M | bochner | open | 平均零のスカラー |
| F271 | stepCurve | statement_ja | JP-13 | B | bochner | open | $m$ 個のセルに割り、値のリスト |
| F272 | stepCurve | proof_ja | 自然さ | B | bochner | open | セル番号を床関数で計算し |
| F273 | stepCurve | gap.note | JP-13 | M | bochner | open | 近似階段。A1–A6 の鎖の起点。 |
| F274 | timeConvL2 | gap.note | JP-13 | M | bochner | open | 再検証で reopen: lane→系列 は #52 処理済みだが「時間軸鏡像」が残存 |
| F275 | timeConvL2_norm_le | proof_ja | JP-13 | B | bochner | open | 単位質量で積分を $\lVert g \rVert$ に潰す。 |
| F276 | timeConvL2_sub_eq_integral | statement_ja | 造語 | B | bochner | open | 軟化の欠損の積分表示 |
| F277 | timeConvL2_sub_eq_integral | proof_ja | JP-13 | B | bochner | open | 一本の積分に合流させ |
| F278 | timeConvL2_sub_le_translation_modulus | statement_ja | 造語 | B | bochner | open | 並進モジュラスによる欠損評価 |
| F279 | timeConvL2_sub_le_translation_modulus | gap.note | JP-14 | M | bochner | open | 再検証で reopen: lane→系列 は #52 処理済みだが「直移植」が残存 |
| F280 | timeConvL2_tendsto_self | statement_ja | JP-13 | B | bochner | open | 半径が $0$ に潰れるとき |
| F281 | timeConvL2_tendsto_self | proof_ja | 造語 | B | bochner | open | 並進モジュラス |
| F282 | timeConvL2_tendsto_self | gap.note | JP-13 | M | bochner | open | 自前で組み上げられている（S1 の礎石 |
| F283 | timeConvL2_weakDeriv_comm | gap.note | JP-14 | M | bochner | open | signature 修正 |
| F284 | timeConvL2_weakDeriv_comm | gap.note | JP-13 | M | bochner | open | 時間軟化理論の心臓部。 |
| F285 | timeMollification_exists | proof_ja | JP-13 | B | bochner | open | **区間 $[0, T]$ への移送**が壁である |
| F286 | timeMollification_exists | gap.note | 造語 | B | bochner | open | S1 スパイクの単一の from-scratch 柱 |
| F287 | timeMollification_of_w1pTime | statement_ja | 自然さ | B | bochner | open | 時間軟化データの構成子 |
| F288 | timeMollification_of_w1pTime | gap.note | JP-13 | M | bochner | open | 下流の配線を書けるようにする |
| F289 | totallyBounded_of_uniform_approx' | proof_ja | JP-16 | M | bochner | open | 有限 $\varepsilon/2$ ネット |
| F290 | translationModulus_zero | statement_ja | 造語 | B | bochner | open | 並進モジュラス |
| F291 | translationModulus_zero | gap.note | JP-13 | M | bochner | open | 連続性論法の錨点。 |
| F292 | w1pTime_continuous_in_H | proof_ja | JP-13 | B | bochner | open | 理論の柱に当たる。 |
| F293 | w1pTime_continuous_in_H | proof_ja | JP-14 | M | bochner | open | months 級の残余 |
| F294 | w1pTime_continuous_in_Vprime | proof_ja | JP-13 | B | bochner | open | du Bois-Reymond の要石 |
| F295 | w1pTime_continuous_in_Vprime | gap.note | JP-14 | M | bochner | open | trace-free）設計 |
| F296 | w1pTime_lineExtension | proof_ja | JP-13 | B | bochner | open | 糊の部品 |
| F297 | weakTimeDerivℝ_even_reflection | proof_ja | JP-13 | B | bochner | open | 微積分学の基本定理の柱が要る。 |
| F298 | weakTimeDerivℝ_even_reflection | gap.note | JP-14 | M | bochner | open | months 級と宣言された残余 |
| F299 | TorusConvectionExtension.antisymmetrizer | statement_ja | 造語 | B | limit-passage | open | 反対称化子 |
| F300 | TorusConvectionExtension.convFormL2_antisymm | statement_ja | 造語 | B | limit-passage | open | 決定移流形式 |
| F301 | TorusConvectionExtension.convFormL2_antisymm | gap.note | JP-13 | M | limit-passage | open | 決定形式の設計上の配当 |
| F302 | TorusConvectionExtension.convFormL2_cont_fixedTest | statement_ja | 造語 | B | limit-passage | open | 結合連続性 |
| F303 | TorusConvectionExtension.convFormL2_cont_fixedTest | gap.note | JP-13 | M | limit-passage | open | 近似列を二つの引数に同時に流し込める |
| F304 | TorusConvectionExtension.convFormL2_def | statement_ja | 造語 | B | limit-passage | open | 決定移流形式 $b$ |
| F305 | TorusConvectionExtension.convFormL2_def | gap.note | JP-14 | M | limit-passage | superseded-by-#52 |  |
| F306 | TorusConvectionExtension.convFormL2_def_eq | statement_ja | 造語 | B | limit-passage | open | 決定移流形式の展開規則 |
| F307 | TorusConvectionExtension.convFormL2_multilinear | statement_ja | 自然さ | M | limit-passage | open | 真の実三重線形写像 |
| F308 | TorusConvectionExtension.convFormL2_multilinear | proof_ja | 自然さ | B | limit-passage | open | カリー化した三重線形写像として束ねられる |
| F309 | TorusConvectionExtension.detDomain | statement_ja | 造語 | B | limit-passage | open | 決定域 $D$ |
| F310 | TorusConvectionExtension.detExtend | statement_ja | 造語 | B | limit-passage | open | 決定拡張 |
| F311 | TorusConvectionExtension.detExtend | proof_ja | 造語 | B | limit-passage | open | テンソル辺貼り合わせ構成 |
| F312 | TorusConvectionExtension.detExtend | gap.note | JP-13 | M | limit-passage | open | 構成の心臓部。 |
| F313 | TorusConvectionExtension.edgeSlot2 | statement_ja | 造語 | B | limit-passage | open | 第二スロット Galerkin 辺 |
| F314 | TorusConvectionExtension.edgeSlot3 | statement_ja | 造語 | B | limit-passage | open | 第三スロット Galerkin 辺 |
| F315 | coeff_zero_outside_box | gap.note | 造語 | B | limit-passage | open | 支持補題 |
| F316 | convBLTgalerkin | proof_ja | JP-13 | B | limit-passage | fixed | P1: F059 と統合適用 |
| F317 | convBLTgalerkin_apply | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F318 | convBLTw | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F319 | convBLTw | proof_ja | 自然さ | B | limit-passage | open | 定数を添えて連続化する |
| F320 | convBLTw_apply | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F321 | convBilL2Sigma | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F322 | convBilL2Sigma | proof_ja | 自然さ | B | limit-passage | open | フィールドごとに充てる。 |
| F323 | convFormFourier_eq_galerkin | proof_ja | JP-13 | B | limit-passage | open | 有限和に潰れる |
| F324 | convFormFourier_eq_galerkin | gap.note | JP-13 | M | limit-passage | open | 有限和の定式化（ODE 層）の橋。 |
| F325 | convFormL2_bound_galerkinTest | proof_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F326 | convFormL2_def_eq_convValW | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F327 | convFormL2_def_eq_convValW | proof_ja | 造語 | B | limit-passage | open | 第三スロット辺 |
| F328 | convFormL2_def_eq_convValW | gap.note | JP-13 | M | limit-passage | open | Fourier 級数の値を繋ぐ橋。 |
| F329 | convFormL2_galerkinTest_dense | gap.note | 造語 | B | limit-passage | open | 決定形式の一意性 |
| F330 | convFormL2_galerkin_pin | statement_ja | JP-14 | B | limit-passage | superseded-by-#52 |  |
| F331 | convFormL2_galerkin_pin | proof_ja | JP-13 | B | limit-passage | open | 箱への潰し |
| F332 | convSummandW | gap.note | JP-13 | M | limit-passage | superseded-by-#52 |  |
| F333 | convSummandW_norm_summable | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F334 | convSummandW_norm_summable | proof_ja | 造語 | B | limit-passage | open | 優関数族 |
| F335 | convSummandW_summable | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F336 | convValW | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F337 | convValW_add_u | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F338 | convValW_add_v | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F339 | convValW_add_w | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F340 | convValW_bound | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F341 | convValW_eq_convFormFourier | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F342 | convValW_eq_convFormFourier | gap.note | JP-13 | M | limit-passage | open | 相殺機構 |
| F343 | convValW_smul_u | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F344 | convValW_smul_v | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F345 | convValW_smul_w | statement_ja | JP-17 | B | limit-passage | superseded-by-#52 |  |
| F346 | dom_summable | statement_ja | 造語 | B | limit-passage | open | 優関数族の総和可能性 |
| F347 | dom_tsum_le | statement_ja | 造語 | B | limit-passage | open | 優関数族の総和の評価 |
| F348 | dom_tsum_le | proof_ja | JP-13 | B | limit-passage | open | 有限和に潰す。 |
| F349 | edge_inf_eq_galerkin_tensor | statement_ja | 造語 | B | limit-passage | open | 辺の重なりの同定 |
| F350 | edge_inf_eq_galerkin_tensor | gap.note | 自然さ | M | limit-passage | open | 使い回している。 |
| F351 | galerkinConvection_antisymm | gap.note | JP-13 | M | limit-passage | open | 相殺機構は同じ。 |
| F352 | galerkinConvection_level_stable | statement_ja | 造語 | B | limit-passage | open | 水準安定性（対称形） |
| F353 | galerkinConvection_level_stable | proof_ja | 造語 | B | limit-passage | open | 単調ステップ |
| F354 | galerkinConvection_level_stable | gap.note | JP-14 | M | limit-passage | superseded-by-#52 |  |
| F355 | galerkinConvection_level_step | statement_ja | 造語 | B | limit-passage | open | 水準安定性（単調ステップ） |
| F356 | isGalerkinTest_add | proof_ja | JP-13 | B | limit-passage | open | 水準の昇格 |
| F357 | isGalerkinTest_zero | gap.note | JP-13 | M | limit-passage | open | 閉性の部品。 |
| F358 | l2coeff | gap.note | 自然さ | M | limit-passage | open | 「係数側の量」として持ち回り |
| F359 | mem_galerkinTestSpan_isTest | proof_ja | JP-14 | M | limit-passage | open | span についての帰納法 |
| F360 | torusConvectionGap_holds | statement_ja | 造語 | B | limit-passage | superseded-by-#52 |  |
| F361 | torusConvectionGap_holds | statement_ja | JP-14 | B | limit-passage | superseded-by-#52 |  |
| F362 | torusConvectionGap_holds | statement_ja | 自然さ | B | limit-passage | superseded-by-#52 |  |
| F363 | torusConvectionGap_holds | proof_ja | 自然さ | B | limit-passage | superseded-by-#52 |  |
| F364 | torusConvectionGap_holds | gap.note | JP-14 | M | limit-passage | superseded-by-#52 |  |
| F365 | torus_weakFormNS_of_strongConvergence | statement_ja | JP-13 | B | limit-passage | open | Aubin–Lions パッケージ |
| F366 | torus_weakFormNS_of_strongConvergence | proof_ja | JP-14 | M | limit-passage | superseded-by-#52 |  |
| F367 | torus_weakFormNS_of_strongConvergence | proof_ja | 造語 | B | limit-passage | open | 一様球有界 |
| F368 | torus_weakFormNS_of_strongConvergence | proof_ja | 自然さ | B | limit-passage | open | パッケージの強収束フィールドの量 |
| F369 | torus_weakFormNS_of_strongConvergence | gap.note | JP-14 | M | limit-passage | open | 極限移行 capstone |
| F370 | velocityProjection_n_eq_of_le | statement_ja | JP-13 | B | limit-passage | open | 帯域水準の昇格 |
| F371 | velocityProjection_n_eq_of_le | gap.note | JP-13 | M | limit-passage | open | ODE を発火させる |
