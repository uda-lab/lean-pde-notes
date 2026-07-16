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
| F011 | exists_galerkin_modewise_extraction | proof_ja | JP-13/造語 | B | compactness | fixed | P1: 証人+帯域水準→打ち切り次数の複合書き換え（F130 と統合適用） |
| F012 | exists_galerkin_modewise_extraction | proof_ja | JP-13 | B | compactness | fixed | P2: エンジン→抽出定理 (with F131/F132, decls.json checked: exists_galerkin_modewise_extraction sig unchanged) |
| F013 | exists_limit_curve_of_galSeq | proof_ja | JP-13 | B | compactness | fixed | P2: 配線の定理→既に得た四つの結果を組み合わせる定理 (merged with F133; kept wikilink targets, edited display text only) |
| F014 | exists_limit_curve_of_galSeq | proof_ja | 自然さ/JP-13 | M | compactness | fixed | P2: エクスポートを添えて→用いて...を構成し (merged with F134's broader fix, same span) |
| F015 | exists_limit_curve_of_galSeq | gap.note | JP-13 | M | compactness | fixed | P2: 取っ手/capstone metaphor removed (merged with F135, same span) |
| F016 | galerkin_u_norm_le | statement_ja | 自然さ | M | compactness | fixed | P2: subsumed by F144's fuller BLOCKING rewrite of the same title span |
| F017 | integral_tail_sq_limit_le | gap.note | JP-13 | M | compactness | fixed | P2: same span as F152 ('...を極限曲線に密輸しない誠実な経路の設計'); resolved together with F152's rewrite of that gap.note sentence |
| F018 | galerkin_test_pairing_lipschitz | statement_ja | 造語/自然さ | A | compactness | fixed | P1: 帯域水準→打ち切り次数（owner 裁定 2026-07-15b、statement_ja + gap.note の 2 箇所） |
| F019 | tail_sq_le_h1EnergySq_div | statement_ja | 造語/自然さ | M | compactness | fixed | P2: 尾部の H¹ 優越→尾部の H^1 エネルギーによる評価; also updated the wikilink display text in integral_tail_sq_galerkin_le.yaml for consistency (decls.json checked: tail_sq_le_h1EnergySq_div sig unchanged) |
| F020 | DivFreeL2 | statement_ja | 自然さ | M | spaces | fixed | P1: statement_ja: 「発散ゼロ性の」→「発散がゼロであることの」. decls.json checked: doc confirms 'Fourier characterisation of div u=0 for L2 vector fields'; meaning preserved. |
| F021 | DivFreeL2 | gap.note | JP-14 | M | spaces | superseded-by-#52 |  |
| F022 | L2VF | gap.note | JP-13 | A | spaces | fixed | P1: gap.note theater metaphor 「主舞台」→「中心」(same span as F110, one edit serves both). |
| F023 | IsGalerkinTest | gap.note | JP-14 | M | capstone-torus | superseded-by-#52 |  |
| F024 | IsGalerkinTest | gap.note | 造語 | M | capstone-torus | fixed | P2: Superseded by F164's rewrite on the same quote/field; applied together. decls.json not applicable (gap.note). |
| F025 | torus3Evolution | statement_ja | 造語 | M | capstone-torus | fixed | P2: テスト級→テスト関数系 also propagated to the two other テスト級 occurrences in the same statement_ja for consistency. decls.json checked (torus3Evolution: Torus3NSForms → DissipativeEvolution). |
| F026 | torus3Evolution | gap.note | JP-14 | M | capstone-torus | superseded-by-#52 |  |
| F027 | ExistsLerayHopf | statement_ja | 自然さ/表記 | M | misc | fixed | P2: subsumed by F179's fuller BLOCKING rewrite of the same title span |
| F028 | LerayHopfNonunique | gap.note | JP-14/自然さ | M | misc | fixed | P2: subsumed by F183's fuller rewrite removing both 'Branch' and '場所取り' in one sentence |
| F029 | lower_bound_from_inverse_square_lifespan | gap.note | JP-14 | M | misc | fixed | P2: Branch→分岐 (merged with F187, preserved '探索期' context info that F187's literal rewrite would have dropped) |
| F030 | mem_velocitySpan_of_fixed | proof_ja | JP-13/借用語彙 | B | projections-galerkin | fixed | P1: 自身を原像として取る形に書き換え（F206 と統合適用） |
| F031 | velocityP_initial_mem | proof_ja | JP-13/借用語彙 | B | projections-galerkin | fixed | P1: u0 自身を取る形に書き換え（F208 と統合適用） |
| F032 | fourierCoeffCLM_apply | gap.note | JP-13/比喩 | M | projections-galerkin | fixed | P2: Combined with F194 (same quote/field, same file); applied one rewrite. |
| F033 | velocityProjection_n_inner_of_fixed | statement_ja | 自然さ | M | projections-galerkin | fixed | P2: Combined with F210 (same quote/field, same file, 截断 already renamed 打ち切り by earlier P1.5 pass); applied one rewrite. |
| F034 | fourierCoeffCLM | statement_ja | 造語/自然さ | M | projections-galerkin | fixed | P2: Combined with F192 (identical quote/field); applied one rewrite. decls.json checked (fourierCoeffCLM: (Fin 3 → ℤ) → L2C →L[ℂ] ℂ, i.e. genuinely a continuous linear functional — statement matches). |
| F035 | velocitySpan | gap.note | JP-13/表記 | M | projections-galerkin | fixed | P1.5: 鏡像→対応物 + ℝ³ 系統（reopen 後 P1.5 で修正） |
| F036 | fourierProjection_n_tendsto | gap.note | 表記/訳語ゆれ | M | projections-galerkin | superseded-by-#52 |  |
| F037 | mem_velocitySpan_iff | gap.note | JP-14/表記 | M | projections-galerkin | fixed | P2: Translated bridge→橋渡し per G4 and the PROTECTED-terms ruling (橋渡し must be used, not deleted); this also resolves F204 (see below). |
| F038 | fourierBox_exhausts | statement_ja | 自然さ | A | projections-galerkin | superseded-by-#52 |  |
| F039 | exists_uniform_subseq_of_lipschitz_family | statement_ja | JP-13/造語 | B | bochner | fixed | PR #57: statement_ja「対角線論法エンジン」を「対角線論法による構成」に置換し機械比喩を除去 |
| F040 | exists_uniform_subseq_of_lipschitz_family | statement_ja | JP-14 | M | bochner | fixed | P1: eventually→ある番号以降で（reopen 後、owner 裁定に従い修正） |
| F041 | exists_uniform_subseq_of_lipschitz_family | gap.note | 造語 | M | bochner | fixed | P1: 載荷点→技術上の要点（owner 裁定 2026-07-15b）+ 同文の帯域水準→打ち切り次数 |
| F042 | exists_Icc_of_compact_subset_Ioo | gap.note | JP-13 | M | bochner | fixed | PR #57: gap.note「同時に収める区間を取る簿記の補題」を「同時に収める区間を取るための補助補題」に置換し比喩を除去 |
| F043 | isWeakTimeDeriv_zero_ae_const | statement_ja | JP-13 | M | bochner | fixed | PR #57: 「du Bois-Reymond の要石」→「du Bois-Reymond 論法の中心的補題」（F263と同一箇所、BLOCKING側の訳語を採用） |
| F044 | w1pTime_continuous_in_H | proof_ja | JP-13 | M | bochner | fixed | PR #57: 「理論の柱に当たる」→「理論の基幹定理に当たる」に修正（F292 と同一箇所を統合修正） |
| F045 | timeConvL2_weakDeriv_comm | gap.note | JP-13 | M | bochner | fixed | PR #57: 「心臓部」→「中心的な結果」（F284と同一文、一括処理） |
| F046 | w1pTime_lineExtension | proof_ja | JP-13 | M | bochner | fixed | PR #57: proof_ja「糊の部品」を「構成に必要な補題」に置換（同一文の「柱」「簿記」比喩も JP-13 一貫性のため合わせて解消：トレースの柱→トレースに関する未証明部分、簿記→管理） |
| F047 | translationModulus_zero | gap.note | 造語 | M | bochner | fixed | PR #57: gap.note「連続性論法の錨点」を「連続性論法における出発点」に置換し航海比喩を除去 |
| F048 | timeMollification_exists | proof_ja | JP-13/自然さ | M | bochner | fixed | PR #57: 「壁である」を「残る問題は…ことである」に書き換え（F285 と同一箇所を統合修正） |
| F049 | hToVprimeCLM | proof_ja | JP-13/自然さ | M | bochner | fixed | PR #57: 「正直な連続線形写像」→「通常の連続線形写像」（F255と同一箇所、BLOCKING側の訳語を採用） |
| F050 | isWeakTimeDerivℝ_smul_cutoff | proof_ja | 自然さ | M | bochner | fixed | PR #57: 「$\psi$ の台が勝つ」→「台は $\psi$ の台に含まれる」に修正（F265 と同一箇所を統合修正） |
| F051 | isWeakTimeDerivℝ_smul_cutoff | gap.note | 自然さ | M | bochner | fixed | PR #57: 「ジャンク値」→「意図した値を表さない場合がある」に修正（F266 と同一箇所を統合修正） |
| F052 | GelfandTriple | gap.note | 自然さ | M | bochner | fixed | PR #57: primal→原空間側に統一しつつ「冗長がない」→「冗長さがない」に修正 |
| F053 | GelfandTriple | statement_ja | JP-14 | M | bochner | fixed | PR #57: 「の primal データ：」→「の原空間側のデータ：」に翻訳（F230と同一箇所） |
| F054 | GelfandTriple | gap.note | JP-14 | M | bochner | fixed | PR #57: 「No-overclaim」→「過剰な主張はしない」に和文化 |
| F055 | aeStronglyMeasurable_of_spaceTimeL2 | gap.note | JP-14 | M | bochner | fixed | PR #57: gap.note の未訳ラベル「no-smuggle」を「余分な仮定を持ち込まない」に和文化 |
| F056 | IsOfDissipativeEvolution | statement_ja | JP-13/造語 | M | bochner | fixed | PR #57: 「忠実性契約」→「忠実性条件」に統一（F232 と統合）。同ファイル gap.note 内の「この契約が」も「この条件が」に同期 |
| F057 | isWeakTimeDeriv_comp_clm | statement_ja | 造語/自然さ | M | bochner | fixed | PR #57: statement_ja「連続線形写像による輸送」を「連続線形写像による押し出し」に置換（最適輸送との混同を回避）。同ファイル群内の関連参照（ofHValuedDeriv.yaml のリンク表示語、w1pTime_lineExtension.yaml の地の文）も一貫して更新 |
| F058 | continuous_translationModulus | statement_ja | 表記(訳語ゆれ) | A | bochner | fixed | PR #57: 並進/平行移動の訳語ゆれをF243の修正と合わせて「平行移動差のノルム」に統一し解消 |
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
| F129 | L2C_norm_sub_fourierProjection_sq | proof_ja | 表記 | B | compactness | fixed | P2: 部分型→箱の補集合を添字集合とする; PROTECTED term 被和項 left untouched per ruling |
| F130 | exists_galerkin_modewise_extraction | proof_ja | JP-13 | B | compactness | fixed | P1: F011 と統合適用 |
| F131 | exists_galerkin_modewise_extraction | proof_ja | JP-13 | B | compactness | fixed | P2: applied together with F012/F132 as one coherent proof_ja rewrite |
| F132 | exists_galerkin_modewise_extraction | proof_ja | 表記 | B | compactness | fixed | P2: Lean identifier moved from proof_ja to gap.note (backticks now only in gap.note, per D3) |
| F133 | exists_limit_curve_of_galSeq | proof_ja | JP-13 | B | compactness | fixed | P2: used F133's phrasing over F013's (cleaner, no residual engineering term); decls.json checked: exists_limit_curve_of_galSeq sig unchanged |
| F134 | exists_limit_curve_of_galSeq | proof_ja | JP-13 | B | compactness | fixed | P2: preserved all three [[wikilink\|LeanName]] targets, edited only display text/connective wording |
| F135 | exists_limit_curve_of_galSeq | gap.note | JP-13 | M | compactness | fixed | P2: used F135's fuller replacement over F015's; consolidated the single gap.note sentence |
| F136 | exists_weak_limit_curve | statement_ja | 自然さ | B | compactness | superseded-by-#52 |  |
| F137 | exists_weak_limit_curve | proof_ja | JP-14 | M | compactness | superseded-by-#52 |  |
| F138 | exists_weak_limit_curve | proof_ja | 造語 | B | compactness | superseded-by-#52 |  |
| F139 | galerkin_test_pairing_lipschitz | statement_ja | 造語 | B | compactness | fixed | P1: F018 と統合適用（帯域水準→打ち切り次数、owner 訂正裁定後の表記）。PR #53 |
| F140 | galerkin_test_pairing_lipschitz | proof_ja | 表記 | B | compactness | fixed | P2: ODE フィールド→Galerkin ODE を用いて; decls.json checked: galerkin_test_pairing_lipschitz sig unchanged |
| F141 | galerkin_test_pairing_lipschitz | proof_ja | 造語 | B | compactness | fixed | P2: 一様球有界→次の一様評価 (display formula already follows inline, adapted wording rather than duplicating the formula per F141's literal suggestion) |
| F142 | galerkin_test_pairing_lipschitz | gap.note | JP-13 | M | compactness | fixed | P2: ODE フィールドが発火する→Galerkin ODE のテスト条件が満たされる; also fixed adjacent unflagged '抽出エンジン'→'抽出定理' in the same sentence for internal consistency with F012/F131's terminology choice |
| F143 | galerkin_u_continuousOn | proof_ja | 表記 | B | compactness | fixed | P2: 前向き微分可能性フィールド→前向き微分可能性 (kept the underlying regularity source, dropped only the Lean-field wording); decls.json checked: galerkin_u_continuousOn sig unchanged |
| F144 | galerkin_u_norm_le | statement_ja | 造語 | B | compactness | fixed | P2: title rewritten to 一様ノルム評価; propagated the rename to two wikilink display texts elsewhere (exists_galerkin_modewise_extraction.yaml, exists_limit_curve_of_galSeq.yaml) that pointed at this declaration using the same flagged term; decls.json checked: galerkin_u_norm_le sig unchanged |
| F145 | galerkin_u_norm_le | proof_ja | 表記 | B | compactness | fixed | P2: エネルギー有界フィールド→エネルギー評価; kept 打ち切り (not 截断) per owner ruling, rejected the literal '截断' in the suggested rewrite text |
| F146 | h1EnergySq_continuousOn_galerkin | proof_ja | JP-13 | B | compactness | fixed | P2: 潰れる→帰着する; '帯域制限されている' phrase left untouched (already correct per owner ruling) |
| F147 | integral_sq_proj_tendsto_zero_of_weak | statement_ja | 造語 | B | compactness | fixed | P2: 一様球有界→「列と極限曲線の一様なノルム有界性（いずれもノルムが M 以下）」（codex 指摘で両仮定の明示に修正。decls.json の署名で両有界性仮定を確認） |
| F148 | integral_sq_proj_tendsto_zero_of_weak | proof_ja | 造語 | B | compactness | fixed | P2: 弱対→基底ベクトルとの内積...弱収束の仮定から収束する |
| F149 | integral_tail_sq_galerkin_le | proof_ja | 表記 | B | compactness | fixed | P2: 解データのH^1正則性フィールド→解データが持つH^1正則性; also fixed the twin unflagged 'フィールド' occurrence later in the same proof_ja ('一様正則性評価フィールド'→'一様正則性評価') for internal consistency |
| F150 | integral_tail_sq_limit_le | proof_ja | JP-13 | B | compactness | fixed | P2: Galerkin側の実数経路は使えない→実数値の尾部評価は直接適用できない; decls.json checked: integral_tail_sq_limit_le sig unchanged |
| F151 | integral_tail_sq_limit_le | proof_ja | 造語 | B | compactness | rejected | 却下: quote 'ENNReal 橋渡し' contains the PROTECTED term 橋渡し (owner ruling: REJECT any finding suggesting its removal). Left the wikilink display text unchanged. |
| F152 | integral_tail_sq_limit_le | gap.note | JP-13 | M | compactness | fixed | P2: 密輸しない誠実な経路→仮定せずに進める経路 |
| F153 | ofReal_tail_sq_eq_tailEnn | statement_ja | 造語 | B | compactness | rejected | 却下: quote '尾部の拡張非負実数橋渡し' contains the PROTECTED term 橋渡し (owner ruling: REJECT any finding suggesting its removal). Left the statement_ja title unchanged. |
| F154 | ofReal_tail_sq_eq_tailEnn | proof_ja | 自然さ | M | compactness | fixed | P2: で実側を書き換え→を用いて実数値の左辺を書き換え |
| F155 | tailEnn_lsc_of_weak | proof_ja | 造語 | B | compactness | fixed | P2: 積添字→成分と箱外格子点の直積を添字集合とする; decls.json checked: tailEnn_lsc_of_weak sig unchanged |
| F156 | tailEnn_lsc_of_weak | gap.note | JP-13 | M | compactness | fixed | P2: 骨組み/回収する→Fatouの補題と同型の議論...弱収束から係数ごとの収束を得る (note: this 骨組み is distinct from the PROTECTED term 骨格, not affected by that ruling) |
| F157 | tail_sq_le_h1EnergySq_div | proof_ja | 表記 | B | compactness | fixed | P2: 補題`H1_tail_bound`に委譲→成分ごとの標準的なFourier尾部評価を適用する (Lean identifier removed from proof_ja); decls.json checked: tail_sq_le_h1EnergySq_div sig unchanged |
| F158 | tail_sq_le_h1EnergySq_div | gap.note | JP-13 | M | compactness | fixed | P2: tsumのジャンク0潰れ→tsum規約のもとで総和不能な場合に値が0となる事態 |
| F159 | tendsto_inner_L2VF_of_tendsto_inner_L2Sigma | statement_ja | 造語 | B | compactness | fixed | P2: テスト級の昇格→弱収束を全L^2テスト関数へ拡張する補題; propagated shortened display text to the wikilink in integral_tail_sq_limit_le.yaml; decls.json checked: tendsto_inner_L2VF_of_tendsto_inner_L2Sigma sig unchanged |
| F160 | tendsto_inner_L2VF_of_tendsto_inner_L2Sigma | gap.note | JP-13 | M | compactness | fixed | P2: 到達可能にする接続部品→弱収束から導く補題 |
| F161 | GalerkinCompactnessPackageFull | statement_ja | JP-16 | B | capstone-torus | fixed | P2: エネルギークラス→エネルギー類 (GLOSSARY canonical term). decls.json checked (GalerkinCompactnessPackageFull: Torus3NSForms → ℝ → ℝ → L2Sigma → Type; terminology-only change, no content impact). |
| F162 | GalerkinCompactnessPackageFull | proof_ja | 造語 | B | capstone-torus | fixed | P2: MODIFIED rewrite: kept 形式束 (protected term — GLOSSARY confirms 散逸発展 is itself defined as an 抽象束, and decls.json confirms torus3Evolution's domain type is literally named Torus3NSForms, i.e. a real bundle type), only removed vague 中核 and programmatic 渡す. Rewrote as 'トーラス領域データと形式束（粘性形式・移流形式・テスト関数族）に汎用構成を適用した略記として定める。' |
| F163 | GalerkinCompactnessPackageFull | gap.note | JP-16 | M | capstone-torus | fixed | P2: エネルギークラス→エネルギー類 in gap.note, per GLOSSARY canonical term. |
| F164 | IsGalerkinTest | gap.note | 造語 | B | capstone-torus | fixed | P2: Applied verbatim; also fixes F024 on the same span. |
| F165 | IsGalerkinTest | gap.note | 自然さ | M | capstone-torus | superseded-by-#52 |  |
| F166 | build_galerkin_package_of_galSeq | proof_ja | 表記 | B | capstone-torus | fixed | P2: Applied verbatim, removes raw Lean identifier rellich_L2Sigma from proof_ja per D3 convention. |
| F167 | build_galerkin_package_of_galSeq | proof_ja | JP-16 | M | capstone-torus | fixed | P2: エネルギークラス→エネルギー類, verb 供給→示す, plus swept the later 'エネルギークラスを持つ' occurrence in the same proof_ja and the wikilink display text エネルギークラスの導出→エネルギー類の導出 for corpus-internal consistency. |
| F168 | build_galerkin_package_of_galSeq | proof_ja | JP-13 | B | capstone-torus | fixed | P2: Applied verbatim, replaces 証明保持構造に詰める with 証明保持型の元を構成する. |
| F169 | build_galerkin_package_of_galSeq | gap.note | 表記 | M | capstone-torus | fixed | P2: Applied verbatim, wraps import in backticks. |
| F170 | build_galerkin_package_of_torus | proof_ja | JP-13 | B | capstone-torus | fixed | P2: MODIFIED: preserved the wikilink target LerayHopf.build_galerkin_package_of_galSeq but changed its display text from 組み立ての中核 (vague 中核) to パッケージの組み立て, matching that target file's own statement_ja label. Removed 渡すだけ per JP-13. |
| F171 | exists_lerayHopf_from_package_full | proof_ja | 表記 | B | capstone-torus | fixed | P2: Applied verbatim, removes フィールド/解構造 Lean-implementation vocabulary from proof_ja. |
| F172 | galSeq_of_torus | proof_ja | 表記 | B | capstone-torus | fixed | P2: Applied (adapted): dropped the raw backticked Lean name `galerkinSolutionData_torus` entirely from proof_ja per D3 (Lean specifics belong in gap.note), replaced 呼ぶ with 適用する. |
| F173 | stokesTestPairing | gap.note | JP-16 | M | capstone-torus | fixed | P2: Removed ジャンク値, kept the parenthetical explanation already present in the file (content was materially the same as the rewrite's target). |
| F174 | stokesTestPairing | gap.note | 自然さ | M | capstone-torus | fixed | P2: Applied with 担う kept (minimal diff) instead of rewrite's 扱う — same meaning, smaller edit. |
| F175 | torus3Evolution | statement_ja | 造語 | B | capstone-torus | rejected | 却下: REJECTED per PROTECTED-terms ruling: quote トーラスの散逸発展の束 uses 束 exactly as GLOSSARY defines 散逸発展 (line 36: '...の抽象束'), and decls.json confirms torus3Evolution's domain type is the real Lean type Torus3NSForms (a genuine bundle), so the finding's premise ('未定義語') does not hold. Did not remove 束. |
| F176 | torus3Evolution | proof_ja | 造語 | B | capstone-torus | fixed | P2: MODIFIED for same reason as F162: kept 形式束 (protected), fixed the vague/programmatic remainder (中核, 渡す). |
| F177 | torus3Evolution | gap.note | 造語 | B | capstone-torus | fixed | P2: Applied, no protected term involved (targets テスト級 wording, not 束). |
| F178 | torus3Evolution | gap.note | 自然さ | M | capstone-torus | superseded-by-#52 |  |
| F179 | ExistsLerayHopf | statement_ja | JP-13 | B | misc | fixed | P2: 最初期スキャフォールド/プレースホルダ解構造→初期段階の暫定的な存在述語...暫定的な解の集合が空でないことを述べる; decls.json checked: ExistsLerayHopf sig unchanged (Ω → Prop) |
| F180 | ExistsLerayHopf | proof_ja | 表記 | B | misc | fixed | P2: Lean struct/file names removed from proof_ja per D3 |
| F181 | ExistsLerayHopf | gap.note | JP-13 | M | misc | fixed | P2: 歴史的スキャフォールドとして残る→開発初期の暫定的な定義として残されている |
| F182 | LerayHopfNonunique | statement_ja | JP-13 | B | misc | fixed | P2: adapted rather than applying the literal rewrite verbatim: kept the mathematical content (相異なる二つの解構造が存在すること) instead of dropping it, only replaced the スキャフォールド metaphor with '開発初期の暫定版'; decls.json checked: LerayHopfNonunique sig unchanged |
| F183 | LerayHopfNonunique | gap.note | JP-13 | M | misc | fixed | P2: Branch B（非一意性方面）の目標文の場所取り→非一意性を扱う将来の作業に備えて置かれた未使用の暫定命題である (subsumes F028) |
| F184 | exists_lerayHopf_torus3_statement | statement_ja | 表記 | B | misc | fixed | P2: 歴史的な目標文（意図的なsorry）→開発初期に置かれた未証明の目標文; decls.json checked: exists_lerayHopf_torus3_statement sig unchanged |
| F185 | exists_lerayHopf_torus3_statement | proof_ja | 表記 | B | misc | fixed | P2: merged with F186 into one coherent proof_ja rewrite; removed raw `sorry` marker and Lean docstring framing |
| F186 | exists_lerayHopf_torus3_statement | proof_ja | JP-13 | B | misc | fixed | P2: 「閉じる」ことは不誠実→暫定述語を自明に充足させても解析的な存在証明にはならない |
| F187 | lower_bound_from_inverse_square_lifespan | gap.note | 自然さ | M | misc | fixed | P2: 爆発レート→爆発率, Branch→分岐 (merged with F029; kept '探索期' modifier that F187's literal text alone would have dropped) |
| F188 | L2VF_ext_componentC_mFourierCoeff | proof_ja | 自然さ | M | projections-galerkin | fixed | P2: Applied within the same proof_ja edit that also swept the two 点別 occurrences in this file (Task 2 overlap). |
| F189 | componentC_mem_fourierSpan | gap.note | JP-13 | M | projections-galerkin | fixed | P2: Applied verbatim. |
| F190 | divFreeL2_iff_divSymbol | gap.note | JP-13 | M | projections-galerkin | fixed | P2: Applied verbatim; 橋 here is a bare metaphor distinct from the protected 橋渡し, so removal is correct. |
| F191 | fourierBox_exhausts | statement_ja | JP-17 | B | projections-galerkin | superseded-by-#52 |  |
| F192 | fourierCoeffCLM | statement_ja | 造語 | B | projections-galerkin | fixed | P2: Duplicate of F034 (same quote, same file/field); one edit covers both. |
| F193 | fourierCoeffCLM | proof_ja | 造語 | B | projections-galerkin | fixed | P2: Applied (adapted phrasing) — removes 汎関数化 coinage from proof_ja. |
| F194 | fourierCoeffCLM_apply | gap.note | JP-13 | M | projections-galerkin | fixed | P2: Duplicate of F032; one edit covers both. |
| F195 | fourierProjection_n_tendsto | proof_ja | 表記 | B | projections-galerkin | fixed | P2: Applied (adapted): replaced 各点収束/渡す framing with 強収束 (the standard operator-theory term matching the underlying mathlib lemma Submodule.starProjection_tendsto_self referenced in gap.note) and 用いる instead of 渡す. Kept both wikilinks. |
| F196 | fourierSpan_hasOrthogonalProjection | proof_ja | JP-13 | B | projections-galerkin | fixed | P2: Applied verbatim. |
| F197 | fourierSpan_iSup_dense | proof_ja | JP-17 | B | projections-galerkin | superseded-by-#52 |  |
| F198 | instHasOrthogonalProjectionRealSubtypeAEEqFunTorus3VelocityValueHaarTorus3MemAddSubgroupL2VFL2Sigma | statement_ja | 表記 | B | projections-galerkin | fixed | P2: Applied verbatim. decls.json checked (instHasOrthogonalProjection...: type is LerayHopf.L2Sigma.HasOrthogonalProjection, confirming this is about direct orthogonal-projection existence on the divergence-free space, matching the rewrite). |
| F199 | instHasOrthogonalProjectionRealSubtypeAEEqFunTorus3VelocityValueHaarTorus3MemAddSubgroupL2VFL2Sigma | proof_ja | JP-13 | B | projections-galerkin | fixed | P2: Applied verbatim. |
| F200 | isClosed_L2Sigma | gap.note | JP-13 | M | projections-galerkin | fixed | P2: Applied (adapted) — also dropped 実装した in favor of 定めた for natural math register, consistent with the rewrite's spirit. |
| F201 | lerayProjection_isSymmetric | gap.note | 造語 | B | projections-galerkin | fixed | P2: MODIFIED to preserve the wikilink to LerayHopf.tendsto_inner_L2VF_of_tendsto_inner_L2Sigma (display text changed from テスト級の昇格 to 補題, content changed from テスト級の昇格 framing to 弱収束を全 L^2 テスト関数へ拡張する). |
| F202 | mem_sigma_of_mem_velocitySpan | statement_ja | 造語 | B | projections-galerkin | fixed | P2: Applied verbatim. decls.json checked (mem_sigma_of_mem_velocitySpan: ∀ n (v : V_n), ↑v ∈ L2Sigma — matches '$V_n$ の各元は発散ゼロ空間に属する'). |
| F203 | mem_sigma_of_mem_velocitySpan | proof_ja | 表記 | B | projections-galerkin | fixed | P2: MODIFIED to preserve the wikilink to LerayHopf.velocitySpan_le_sigma (display text 包含 kept, followed by the explicit inclusion formula). |
| F204 | mem_velocitySpan_iff | gap.note | 自然さ | M | projections-galerkin | rejected | 却下: REJECTED in favor of F037's rewrite on the same quote/span: owner ruling explicitly says untranslated bridge SHOULD be translated to 橋渡し (G4), which is what F037 does; F204's alternative (paraphrase avoiding bridge language entirely) was not applied since F037 already resolves the untranslated-English problem correctly. |
| F205 | mem_velocitySpan_of_fixed | statement_ja | 自然さ | B | projections-galerkin | fixed | P2: Applied (adapted): translated bridge→橋渡し per G4/PROTECTED ruling instead of dropping it; also fixed the dangling '像に属する' subject to '$V_n$ に属する' for clarity. decls.json checked (mem_velocitySpan_of_fixed: ∀ n, ∀ x ∈ L2Sigma, P_n x = x → x ∈ velocitySpan n — matches '発散ゼロで、打ち切っても変わらない場は V_n に属する'). |
| F206 | mem_velocitySpan_of_fixed | proof_ja | JP-13 | B | projections-galerkin | fixed | P1: F030 と統合適用 |
| F207 | velocityP_fixes_span | statement_ja | 自然さ | B | projections-galerkin | fixed | P2: Applied (adapted): translated bridge→橋渡し, added the fixing operator P_n for clarity. decls.json checked (velocityP_fixes_span: ∀ n (v : V_n), P_n ↑v = ↑v — matches). |
| F208 | velocityP_initial_mem | proof_ja | JP-13 | B | projections-galerkin | fixed | P1: F031 と統合適用 |
| F209 | velocityProjection_n_comp_of_le | statement_ja | JP-13 | B | projections-galerkin | fixed | P2: Applied (adapted, 截断→打ち切り per binding ruling). decls.json checked (velocityProjection_n_comp_of_le: n ≤ m → P_n(P_m u) = P_n u — matches 'B_m で打ち切ってから B_n で打ち切っても結果は変わらない'). |
| F210 | velocityProjection_n_inner_of_fixed | statement_ja | JP-13 | B | projections-galerkin | fixed | P2: Combined with F033 (same file/field); resulting statement_ja: '帯域制限テストとの内積は打ち切り前後で一致する'. |
| F211 | velocitySpan | gap.note | 自然さ | M | projections-galerkin | fixed | P1.5: F035 と統合適用（P1.5） |
| F212 | velocitySpanToSigma | statement_ja | 表記 | B | projections-galerkin | fixed | P2: Applied verbatim. decls.json checked (velocitySpanToSigma: (n) → V_n → L2Sigma — matches 'V_n から発散ゼロ空間への埋め込み'). |
| F213 | velocitySpanToSigma | proof_ja | JP-17 | B | projections-galerkin | fixed | P2: Applied verbatim (removes 台/部分型 Lean vocabulary from proof_ja). |
| F214 | velocitySpanToSigma | gap.note | JP-13 | M | projections-galerkin | fixed | P2: Applied (adapted): file already used 系統 (not lane/レーン) from the earlier P1.5 rename, so kept that and the existing `galerkinSpanToSigma` backtick reference; only removed the bare metaphor 型の橋 (not the protected 橋渡し — this was plain 橋, fair game). |
| F215 | velocitySpanToSigma_add | proof_ja | 表記 | B | projections-galerkin | fixed | P2: Applied verbatim (removes 部分型の外延性 Lean vocabulary). |
| F216 | velocitySpanToSigma_coe | statement_ja | JP-17 | B | projections-galerkin | fixed | P2: Applied verbatim. decls.json checked (velocitySpanToSigma_coe: ↑(velocitySpanToSigma n v) = ↑v — matches '包含写像による像は周囲空間では元の要素に一致する'). |
| F217 | velocitySpanToSigma_coe | proof_ja | 表記 | B | projections-galerkin | fixed | P2: Applied verbatim (removes `rfl` tactic name from proof_ja). |
| F218 | velocitySpanToSigma_smul | proof_ja | 表記 | B | projections-galerkin | fixed | P2: Applied verbatim (removes 部分型の外延性). |
| F219 | velocitySpan_hasOrthogonalProjection | proof_ja | JP-13 | B | projections-galerkin | fixed | P2: Applied verbatim. |
| F220 | velocitySpan_le_sigma | gap.note | JP-13 | M | projections-galerkin | fixed | P2: Applied verbatim (removes 配当 metaphor). |
| F221 | Bochner.ContDiffBump.isTimeMollifier | proof_ja | 自然さ | B | bochner | fixed | PR #57: 「フィールドごとに充てるだけ」→「順に適用するだけ」に修正しLean実装語を除去 |
| F222 | Bochner.ContDiffBump.isTimeMollifier | gap.note | JP-13 | M | bochner | fixed | PR #57: 「供給源」「半径を潰す」→「具体例である」「半径が $0$ に収束する」に修正 |
| F223 | Bochner.IsTimeMollifier | proof_ja | 自然さ | B | bochner | fixed | PR #57: 「四条件をフィールドとして束ねた述語構造である」→「上の四条件の連言として定義する」 |
| F224 | Bochner.WeakLimitToolkit.cauchySeq_inner_extend | proof_ja | 造語 | B | bochner | fixed | PR #57: 「一様球有界」→「ノルムが一様に $M$ 以下であるという仮定」に修正（statement_ja の $\lVert x_k \rVert \le M$ に対応） |
| F225 | Bochner.WeakLimitToolkit.cauchySeq_of_equiLipschitz_of_dense | statement_ja | 造語 | B | bochner | fixed | P1: #52（等→同程度 Lipschitz）+ P1（「連続（性）」付与、owner 裁定）で解消 |
| F226 | Bochner.WeakLimitToolkit.cauchySeq_of_equiLipschitz_of_dense | proof_ja | 造語 | B | bochner | fixed | P1: #52（等→同程度 Lipschitz）+ P1（「連続（性）」付与、owner 裁定）で解消 |
| F227 | Bochner.WeakLimitToolkit.exists_mem_of_ae_full | statement_ja | 自然さ | M | bochner | fixed | PR #57: statement_ja「a.e. に成り立つ集合 $S$」を「ほとんど至る所の点を含む集合 $S$」に置換し係り受けを自然化 |
| F228 | Bochner.WeakLimitToolkit.exists_weak_limit_in_submodule | statement_ja | 自然さ | M | bochner | fixed | PR #57: statement_ja「すべてのテスト $z$ に対し対の列が Cauchy」を「任意の $z$ に対して内積値の列が Cauchy」に置換し内積値であることを明示 |
| F229 | Bochner.WeakLimitToolkit.exists_weak_limit_in_submodule | proof_ja | 造語 | B | bochner | fixed | PR #57: proof_ja「球有界から $M$ 有界性が従う」を監査者提示の式付き説明に置換し未確立語「球有界」「$M$ 有界性」を解消 |
| F230 | GelfandTriple | statement_ja | JP-14 | B | bochner | fixed | PR #57: F053と同一箇所。primal→原空間側に翻訳し dual との対比を保持 |
| F231 | GelfandTriple | proof_ja | 自然さ | B | bochner | fixed | PR #57: proof_ja の「構造（型とインスタンス）」「フィールドに持つ構造」等 Lean 固有語を除去し、実 Hilbert 空間・単射性・稠密値域性を述べる数学文に書き換え（束ねた、は保護語のため維持） |
| F232 | IsOfDissipativeEvolution | statement_ja | 造語 | B | bochner | fixed | PR #57: 直後の文で条件の中身を明示済みのため、契約→条件への用語修正で対応（F056 と同一） |
| F233 | IsOfDissipativeEvolution | proof_ja | 自然さ | B | bochner | fixed | PR #57: 「型の等しさとインスタンスの異型等式」→「ピボット空間と Hilbert 空間構造の一致」に修正。Lean 固有の cast/HEq 詳細は既に gap.note 側にあるためそちらは維持 |
| F234 | IsWeakTimeDeriv | proof_ja | 造語 | B | bochner | fixed | PR #57: 「（全導関数込みで）消える」→「端点の近傍で恒等的に零なので」に書き換え、未確立語「全導関数」を除去 |
| F235 | IsWeakTimeDerivℝ | gap.note | 造語 | B | bochner | fixed | PR #57: 「Fubini 障害」→「Fubini の定理を適用する際の障害」に修正 |
| F236 | TimeMollification | statement_ja | 自然さ | B | bochner | fixed | PR #57: 「をフィールドとして束ねる」→「を一つのデータとしてまとめる」 |
| F237 | TimeMollification | proof_ja | 自然さ | B | bochner | fixed | PR #57: 「六つのフィールド」「構造」表現を除去し、内訳を明示した「まとめたデータとして定める」に書き換え |
| F238 | W1pTime | statement_ja | 自然さ | B | bochner | fixed | PR #57: statement_ja の「フィールドは、」→「このデータは、」に修正 |
| F239 | W1pTime | proof_ja | 自然さ | B | bochner | fixed | PR #57: 「フィールドに持つ構造として定める」→「上記の四つのデータと条件を満たす対として定める」に修正 |
| F240 | aeStronglyMeasurable_of_spaceTimeL2 | proof_ja | JP-13 | B | bochner | fixed | PR #57: proof_ja「二段の一般論を直列に適用する」を「二つの一般定理を順に適用する」に置換し回路比喩を除去 |
| F241 | aeStronglyMeasurable_of_spaceTimeL2 | gap.note | JP-13 | M | bochner | fixed | PR #57: gap.note「可測性は別口で供給されるべき欠けた柱」を「可測性は別に仮定すべき条件」に置換し建築・口語比喩を除去（F055 と同一文で合わせて修正） |
| F242 | continuousOn_primitive_of_integrableOn | statement_ja | 自然さ | M | bochner | fixed | PR #57: statement_ja「上区間可積分な」を「上で区間可積分な」に置換し脱落した助詞を補完 |
| F243 | continuous_translationModulus | statement_ja | 造語 | B | bochner | fixed | PR #57: 「並進モジュラス」（未確立造語）→「平行移動差のノルム」に変更し、proof_ja の「平行移動の連続性」参照と統一 |
| F244 | dist_toLp_stepCurve | gap.note | JP-13 | M | bochner | fixed | PR #57: 「形式へ戻す橋」→「形式へ書き換えるための補題」（橋渡し以外の一般比喩のため保護語に該当せず） |
| F245 | exists_Icc_of_compact_subset_Ioo | statement_ja | JP-17 | B | bochner | fixed | PR #57: statement_ja「閉区間による分離」を「閉区間への包含」に置換（記述内容は分離でなく包含のため） |
| F246 | exists_Icc_of_compact_subset_Ioo | gap.note | JP-13 | M | bochner | fixed | PR #57: F042 と同一文の修正で解消（簿記比喩を除去） |
| F247 | exists_subseq_tendsto_eLpNorm_of_totallyBounded | gap.note | JP-13 | M | bochner | fixed | PR #57: 「A1–A6 の鎖の出口」→「A1–A6 から収束部分列を得る最終段階」に修正 |
| F248 | exists_uniform_subseq_of_lipschitz_family | statement_ja | JP-13 | B | bochner | fixed | PR #57: F039 と同一箇所の修正で解消（エンジン比喩を除去） |
| F249 | exists_uniform_subseq_of_lipschitz_family | statement_ja | JP-14 | B | bochner | fixed | P1: F040 と統合適用 |
| F250 | exists_uniform_subseq_of_lipschitz_family | statement_ja | 造語 | B | bochner | fixed | P1: #52（等→同程度 Lipschitz）+ P1（「連続（性）」付与、owner 裁定）で解消 |
| F251 | exists_uniform_subseq_of_lipschitz_family | proof_ja | 造語 | B | bochner | fixed | PR #57: proof_ja「第二段（一様 Cauchy 化）」を「第二段（部分列が一様 Cauchy であることの証明）」に置換し「〜化」複合語を解消 |
| F252 | exists_uniform_subseq_of_lipschitz_family | gap.note | 造語 | B | bochner | fixed | P1: F041 と統合適用 |
| F253 | exists_unitMass_weight | gap.note | JP-13 | M | bochner | fixed | PR #57: gap.note「要石で「a.e. 定数の値」を汲み出す」を「議論で中心的な役割を果たし、a.e. 定数の値を定める」に置換し建築・採取の比喩を除去 |
| F254 | hToVprimeCLM | statement_ja | 自然さ | B | bochner | rejected | 却下: 束（bundled）系の語は owner 裁定（F071 系）で保護されており、姉妹ファイル（GelfandTriple 等）の「束ねられた連続線形埋め込み」とも整合させるため原文を維持（codex 事前レビュー指摘で復元） |
| F255 | hToVprimeCLM | proof_ja | JP-13 | B | bochner | fixed | PR #57: F049と同一箇所。「正直な」→「通常の」に統一 |
| F256 | hToVprimeCLM_apply | statement_ja | 自然さ | B | bochner | fixed | PR #57: 「CLM 版と裸の埋め込み」→「連続線形写像としての埋め込みと点ごとに定めた埋め込み」 |
| F257 | integrable_timeMollifier_smul_translate | gap.note | JP-14 | M | bochner | fixed | PR #57: 「side condition なしで」→「追加条件なしで」に翻訳 |
| F258 | isCompact_stepCurve_toLp | proof_ja | 造語 | B | bochner | fixed | PR #57: proof_ja「値リストから類への組み立て写像」を「$K^m$ の元（値の組）にステップ曲線の $L^p$ 類を対応させる写像」に置換し計算機語彙を排除（「値リスト」の他の出現も「値の組」に統一） |
| F259 | isWeakTimeDeriv_primitive | statement_ja | JP-14 | B | bochner | fixed | PR #57: 「分布的 FTC」→「分布の意味での微積分学の基本定理」 |
| F260 | isWeakTimeDeriv_primitive | proof_ja | 自然さ | M | bochner | fixed | PR #57: 「`sorry`で開けてある」→「`sorry`として未証明のまま残されている」 |
| F261 | isWeakTimeDeriv_primitive | gap.note | JP-14 | M | bochner | fixed | PR #57: quote中の lane は現行では既に系統に置換済みだったため「閉じている」→「完了している」のみ適用 |
| F262 | isWeakTimeDeriv_unique | gap.note | JP-14 | M | bochner | fixed | PR #57: 「body コメント」→「定理本体のコメント」 |
| F263 | isWeakTimeDeriv_zero_ae_const | statement_ja | JP-13 | B | bochner | fixed | PR #57: F043と同一箇所を一括修正。同ファイル内 gap.note の同種比喩「$V'$ 値良い代表元の要石」も一貫して「中心的な補題」に修正 |
| F264 | isWeakTimeDerivℝ_comp_clm | proof_ja | JP-13 | B | bochner | fixed | PR #57: 「全直線への移植」→「と同様に、全直線上の積分と $L$ を交換し」に書き換えて工学比喩を除去 |
| F265 | isWeakTimeDerivℝ_smul_cutoff | proof_ja | JP-13 | B | bochner | fixed | PR #57: F050 と同一箇所。積 $\chi\psi$ の台の包含関係を明示する表現に修正 |
| F266 | isWeakTimeDerivℝ_smul_cutoff | gap.note | JP-13 | M | bochner | fixed | PR #57: F051 と同一箇所。プログラミング語彙を除去 |
| F267 | ofDissipativeEvolution | statement_ja | 造語 | B | bochner | fixed | PR #57: statement_ja「忠実性契約」を「散逸発展との整合条件」に置換（ソフトウェア契約の比喩を除去、「橋渡し」は保護語のため維持） |
| F268 | ofDissipativeEvolution | proof_ja | 自然さ | B | bochner | fixed | PR #57: proof_ja「フィールドに詰めて」を「三つ組を定め」に置換。同ファイルの「契約」表現（proof_ja「契約の各連言」、gap.note「契約付きの依存対」）も F267 の呼称変更に合わせ「条件」「整合条件付き」に統一 |
| F269 | ofHValuedDeriv | gap.note | JP-14 | M | bochner | fixed | PR #57: gap.note「primal 定義」を「基本となる定義」に置換し未訳英語形容詞を解消 |
| F270 | primitive_baseA_props | statement_ja | 自然さ | M | bochner | fixed | PR #57: 「平均零のスカラー」→「平均が零であるスカラー値関数」 |
| F271 | stepCurve | statement_ja | JP-13 | B | bochner | fixed | PR #57: statement_ja「セル」「値のリスト」を「小区間」「値の列」に置換し計算機語彙を排除 |
| F272 | stepCurve | proof_ja | 自然さ | B | bochner | fixed | PR #57: proof_ja「セル番号を床関数で計算し」を「各 $t$ の属する小区間を床関数で定め」に置換し実装手順的表現を排除（同ファイル内「セル」を一貫して「小区間」に統一） |
| F273 | stepCurve | gap.note | JP-13 | M | bochner | fixed | PR #57: gap.note「近似階段。A1–A6 の鎖の起点」を「A1–A6 の近似論法の出発点」に置換し比喩を除去 |
| F274 | timeConvL2 | gap.note | JP-13 | M | bochner | fixed | PR #57: 「lane」は既に「系統」へ修正済みだったため、残る「時間軸鏡像」を「時間変数に対応する類似物」に修正 |
| F275 | timeConvL2_norm_le | proof_ja | JP-13 | B | bochner | fixed | PR #57: proof_ja「積分を $\lVert g \rVert$ に潰す」を監査者提示の「積分が $\lVert g\rVert$ に等しいことを得る」に置換し口語的動詞を除去 |
| F276 | timeConvL2_sub_eq_integral | statement_ja | 造語 | B | bochner | fixed | PR #57: 「軟化の欠損の積分表示」→「軟化による近似誤差の積分表示」。gap.note の「欠損」「並進モジュラス」も同種として一貫修正 |
| F277 | timeConvL2_sub_eq_integral | proof_ja | JP-13 | B | bochner | fixed | PR #57: 「一本の積分に合流させ」→「積分の線形性により一つの積分として書き」 |
| F278 | timeConvL2_sub_le_translation_modulus | statement_ja | 造語 | B | bochner | fixed | PR #57: 「並進モジュラスによる欠損評価」→「並進差のノルムによる近似誤差の評価」に修正。proof_ja のリンク表示語・gap.note の「欠損」も同期 |
| F279 | timeConvL2_sub_le_translation_modulus | gap.note | JP-14 | M | bochner | fixed | PR #57: 「lane」は既に「系統」へ修正済みだったため、残る「直移植」を「〜と同様である」に修正（F278 と統合編集） |
| F280 | timeConvL2_tendsto_self | statement_ja | JP-13 | B | bochner | fixed | PR #57: 「半径が $0$ に潰れる」→「半径が $0$ に収束する」に修正 |
| F281 | timeConvL2_tendsto_self | proof_ja | 造語 | B | bochner | fixed | PR #57: 「並進モジュラス」→「並進差のノルム」に修正。同ファイル内の全出現とリンク表示語を同期 |
| F282 | timeConvL2_tendsto_self | gap.note | JP-13 | M | bochner | fixed | PR #57: 「自前で組み上げられている（S1 の礎石」→「本章で証明している（S1 の基礎となる結果」に修正。並進モジュラス表記も同期 |
| F283 | timeConvL2_weakDeriv_comm | gap.note | JP-14 | M | bochner | fixed | PR #57: 「signature 修正」→「定理の型の修正」 |
| F284 | timeConvL2_weakDeriv_comm | gap.note | JP-13 | M | bochner | fixed | PR #57: F045と同一箇所を一括で「時間軟化理論の中心的な結果。」に修正 |
| F285 | timeMollification_exists | proof_ja | JP-13 | B | bochner | fixed | PR #57: 壁の比喩を除去し、後続の「注入」「壊す」も比喩色を弱めて統一（生じさせる／余分な項を生じさせない） |
| F286 | timeMollification_exists | gap.note | 造語 | B | bochner | fixed | PR #57: 「from-scratch 柱」→「既存の結果からは直接得られない唯一の未証明事項」に修正。同文中の「days」も「数日」に翻訳し一貫させた |
| F287 | timeMollification_of_w1pTime | statement_ja | 自然さ | B | bochner | fixed | PR #57: statement_ja「時間軟化データの構成子」を「時間軟化データの選択」に置換（Lean constructor の直訳を排除、proof_ja の「選択」と整合） |
| F288 | timeMollification_of_w1pTime | gap.note | JP-13 | M | bochner | fixed | PR #57: gap.note「下流の配線を書けるようにする」を「後続の定理を記述できるようにする」に置換し配線比喩・未訳語 constructor を除去（F287 の呼称変更に合わせ「構成子」も「選択」に統一） |
| F289 | totallyBounded_of_uniform_approx' | proof_ja | JP-16 | M | bochner | fixed | PR #57: GLOSSARY 標準表記に合わせ「有限 $\varepsilon/2$ ネット」→「有限 $\varepsilon/2$-網」、同文中の「$\varepsilon$ ネット」も「$\varepsilon$-網」に統一 |
| F290 | translationModulus_zero | statement_ja | 造語 | B | bochner | fixed | PR #57: statement_ja「並進モジュラス」を「並進差のノルム」に置換（未確立の造語を具体的な量の記述に） |
| F291 | translationModulus_zero | gap.note | JP-13 | M | bochner | fixed | PR #57: F047 と同一文の修正で解消（錨点比喩を除去） |
| F292 | w1pTime_continuous_in_H | proof_ja | JP-13 | B | bochner | fixed | PR #57: F044 と同一箇所。建築比喩を除去し「基幹定理」に統一 |
| F293 | w1pTime_continuous_in_H | proof_ja | JP-14 | M | bochner | fixed | PR #57: 「months 級の残余」→「数か月規模の作業を要する未証明事項」に翻訳 |
| F294 | w1pTime_continuous_in_Vprime | proof_ja | JP-13 | B | bochner | fixed | PR #57: 「du Bois-Reymond の要石」→「du Bois-Reymond 論法の中心的補題」（F043/F263と同一訳語で統一） |
| F295 | w1pTime_continuous_in_Vprime | gap.note | JP-14 | M | bochner | fixed | PR #57: 「（trace-free）」は直前の日本語表現と重複する未訳英語のため削除（「トレースを用いない」を追加すると重複になるため） |
| F296 | w1pTime_lineExtension | proof_ja | JP-13 | B | bochner | fixed | PR #57: F046 と同一箇所の修正で解消。同文の「連続線形輸送」も isWeakTimeDeriv_comp_clm.yaml（F057）の呼称変更に合わせ「連続線形写像による押し出し」に統一 |
| F297 | weakTimeDerivℝ_even_reflection | proof_ja | JP-13 | B | bochner | fixed | PR #57: 「微積分学の基本定理の柱が要る」→「微積分学の基本定理が必要である」に修正 |
| F298 | weakTimeDerivℝ_even_reflection | gap.note | JP-14 | M | bochner | fixed | PR #57: 「months 級と宣言された残余」→「数か月規模の作業を要すると見積もられた未証明事項」に翻訳。同文中の「同じ柱」も「同種の残課題」に修正し一貫させた |
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
| F358 | l2coeff | gap.note | 自然さ | M | limit-passage | fixed | P1.5: 参照表示語「水準の昇格」→「打ち切り次数を増やしたときの不変性」（isGalerkinTest_add、Copilot 指摘契機） |
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
| F370 | velocityProjection_n_eq_of_le | statement_ja | JP-13 | B | limit-passage | fixed | P1.5: 「帯域水準の昇格」→「打ち切り次数を増やしたときの不変性」（velocityProjection_n_eq_of_le statement_ja） |
| F371 | velocityProjection_n_eq_of_le | gap.note | JP-13 | M | limit-passage | fixed | P1.5: 「ODE を発火させる」→「Galerkin ODE を適用可能にする」（同 gap.note） |
