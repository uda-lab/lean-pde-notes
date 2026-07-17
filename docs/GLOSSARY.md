# GLOSSARY — lean-pde-notes 用語集

Leray–Hopf 形式化（`uda-lab/lean-pde`）の注釈コーパスで使う英日訳語対応表。
翻訳作業者はこの表を参照し、確立訳語を使うこと。新語が必要な場合は本表に追記して PR に含めること。

`forbidden` 列：よくある誤訳・禁止訳（`glossary_lint.py` が警告する）。
`⚠要確認` マーク：訳語が暫定・文脈依存の可能性あり。

**使い方**:
- `statement_ja` / `proof_ja` に英語原語を使う場合はカナ・日本語と併記推奨。
- 列見出しの意味: `English term` = 英語（Lean コード中の名前含む）、`日本語訳` = 確立訳、`Lean 識別子例` = 代表的な Lean 名、`forbidden` = 禁止訳・非推奨表現。

<!-- ------------------------------------------------------------------ -->

| English term | 日本語訳 | Lean 識別子例 | 備考 | forbidden |
|---|---|---|---|---|
| weak solution | 弱解 | `LerayHopfSolutionFull` | Leray–Hopf 弱解。証明保持型構造体として定義 | 「弱い解」 |
| energy inequality | エネルギー不等式 | `energy_ineq` | `½‖u(t)‖² ≤ ½‖u(s)‖² − ν∫‖∇u‖²` | 「エネルギー不等号」 |
| energy identity | エネルギー恒等式 | `abstract_galerkin_energy_identity` | ODE 法則から導く等号版 | 「エネルギー等式」 |
| divergence-free | 発散ゼロ | `L2Sigma`, `L2Sigma_R3` | 「ソレノイダル (solenoidal)」とも。T³ では div ⊂ Fourier 核の交叉として定義 | 「発散なし」、「無発散」 |
| mollifier | 軟化子 | `TimeConvolution` | C^∞ コンパクト台の近似恒等核 | 「正則化核」⚠要確認 |
| Galerkin approximation | Galerkin 近似 | `GalerkinSolutionData`, `GalerkinSolutionData_R3` | 有限次元 ODE 族による近似手順 | 「ガレルキン近似」（カナ表記可・英字と統一を推奨） |
| Galerkin scheme | Galerkin スキーム | `R3GalerkinScheme`, `velocityProjection_n` | 近似射影族の束 | |
| weak convergence | 弱収束 | `tendsto_nhdsWithin_atTop` | Hilbert 空間での弱位相での収束 | 「弱い収束」 |
| strong convergence | 強収束 | | L² ノルム収束 | 「強い収束」 |
| weak-* convergence | 弱\*収束 | | 双対空間での弱\*位相での収束 ⚠要確認 | |
| compact embedding | コンパクト埋め込み | `rellich_seq_compact`, `rellich_L2Sigma` | `H¹ ↪ L²` の Rellich–Kondrachov 埋め込み | 「コンパクト的埋め込み」 |
| precompact | 前コンパクト | `H1_ball_totallyBounded` | 閉包がコンパクト。本形式化では「全有界 (totally bounded)」として扱う。「相対コンパクト」は同義の正しい数学用語であり誤りではないが、本コーパスでは訳語統一のため「前コンパクト」を house style として優先する（issue #67：forbidden 対象からは外す） | |
| totally bounded | 全有界 | `Metric.totallyBounded_iff` | 任意の ε>0 に対し有限 ε-網をもつ | |
| compact operator | コンパクト作用素 | `isCompactOperator_of_locallyCompactSpace_dom` | 有界集合の像が前コンパクト（その閉包がコンパクト）であるような作用素。像そのものがコンパクトとは限らない点に注意（issue #67：旧記述「コンパクトな像へ送る」は誤り） | 「コンパクト型作用素」、「有界集合をコンパクトな像へ送る作用素」 |
| compact support | コンパクト台 | `tsupport ψ ⊆ Set.Ioo 0 T` | 関数が零でない集合の閉包がコンパクト | 「有界台」⚠要確認 |
| orthogonal projection | 直交射影 | `orthogonalProjectionOnto`, `HasOrthogonalProjection` | 閉部分空間への直交射影作用素 | 「直交投影」 |
| Leray projection | Leray 射影 | `lerayProjection`, `lerayProjection_R3` | `L²` 上の発散ゼロ部分空間への直交射影 | |
| Hilbert space | Hilbert 空間 / ヒルベルト空間 | `InnerProductSpace`, `CompleteSpace` | 内積完備空間。略称 H | 「ヒルベルト空間」（カナ・英字どちらも可） |
| Sobolev space | Sobolev 空間 / ソボレフ空間 | `h1EnergySq`, `memH1VF_R3` | `H^s` または `W^{k,p}`。本形式化では H¹ が主役 | 「ソボレフ空間」（カナ可） |
| dissipative evolution | 散逸発展 | `DissipativeEvolution` | `H + reg + viscousForm + convForm + isTest` の抽象束 | |
| pivot Hilbert space | ピボット Hilbert 空間 | `DissipativeEvolution.H` | Gelfand 三つ組の中間 H | |
| Gelfand triple | Gelfand 三つ組 | `Bochner.GelfandTriple` | `V ↪ H ↪ V'`。主線の束は `reg` で代替；抽象 Bochner 層では明示的に採用 | 「ゲルファント三つ組」 |
| regularity functional | 正則性汎関数 | `DissipativeEvolution.reg`, `h1EnergySq`, `viscousFormSq` | `reg(u)` のレベル集合コンパクト性 ⇒ Rellich | |
| viscous form | 粘性形式 | `DissipativeEvolution.viscousForm`, `stokesTestPairing`, `stokesTestPairing_R3` | 抽象散逸発展 `DissipativeEvolution` の `viscousForm` は型 `H → H → ℝ` の非スケール双線形形式で、具体的な勾配積分則は課さない。具体的な Fourier 実現である `stokesTestPairing`/`stokesTestPairing_R3` がこれを `a(u,v)=∫∇u:∇v` として与える（「Stokes pairing」行を参照）。`ν` はいずれの定義にも含まれず、弱形式 `WeakFormNS` や粘性散逸形式 `viscousFormSq` など消費側が外側から掛ける（issue #67；codex review PR #80） | 「`ν∫∇u:∇v` を粘性形式自体の定義とする言い換え」、「抽象 `viscousForm` を具体的な `∫∇u:∇v` と同一視する言い換え」 |
| convection form | 移流形式 | `convForm`, `convIntegralSchwartz`, `galerkinConvection` | `b(u,v,w) = ∫(u·∇)v·w`（反対称 `b(u,v,w) = −b(u,w,v)`） | |
| weak formulation | 弱形式 | `WeakFormNS` | Navier–Stokes 方程式の弱積分形式 | 「弱い定式化」 |
| test function | テスト関数 | `DissipativeEvolution.isTest`, `IsSchwartzDivFree_R3` | 弱形式で積分のパートナーとなる滑らかな関数。「試験関数」は数学的に誤りではない標準訳語だが、本コーパスでは統一のため「テスト関数」を house style として優先する（issue #67：forbidden 対象からは外す） | |
| Schwartz function | Schwartz 関数 | `SchwartzMap`, `𝓢(ℝ³,ℝ)` | 急減少滑らか関数。ℝ³ の弱発散定義に使用 | |
| weak divergence | 弱発散 | `divTestFunctional`, `L2Sigma_R3` | 超関数的発散ゼロ：`∀φ∈𝓢, ∫u·∇φ=0` | |
| Fourier coefficient | Fourier 係数 | `mFourierCoeff3` | 本形式化では T³ の離散 Fourier 係数を直接使用 | |
| Fourier truncation | Fourier 打ち切り | `fourierProjection`, `velocityProjection_n` | 箱領域内のモードのみ保持する有限次元射影。操作は「打ち切り」「打ち切り次数」、結果の性質は「帯域制限されている」（issue #51 の owner 裁定） | 「截断」、「裁断」 |
| Fourier truncation residual | Fourier 打ち切り残差 | `L2C_norm_sub_fourierProjection_sq` | $u - P_N u$。文脈が明らかなら単に「打ち切り残差」。非形式的な言い換えは「高周波成分」、直交分解は「打ち切り部分と直交残差」（issue #56） | 「尾部」 |
| out-of-box Fourier coefficient square sum | 周波数箱外の Fourier 係数二乗和 | `tailEnn_lsc_of_weak` | $\sum_{k \notin B_N} \lvert\hat u(k)\rvert^2$。添字付き族は「周波数箱外の Fourier 係数二乗族」（issue #56） | |
| spatial exterior part | 球外部分 | `tailVF` | 半径 $R$ の閉球の補集合への制限。操作は「球外制限」、分解は「球内・球外分解」。物理空間の叙述では「裾」「tail」も許容（issue #56） | |
| limit passage | 極限移行 | `galerkin_limit_passage`, `galerkin_limit_passage_R3` | Galerkin 近似の極限で非線形項を移行する操作 | 「極限の移行」 |
| Aubin–Lions lemma | Aubin–Lions 補題 | `aubin_lions`, `aubin_lions_R3` | 時間コンパクト性：`L²(0,T;V)∩W^{1,q}(0,T;V') ↪ L²(0,T;H)` がコンパクト | |
| Rellich–Kondrachov theorem | Rellich–Kondrachov 定理 | `rellich_seq_compact` | `H¹(T³) ↪ L²(T³)` がコンパクトである定理 | 「Rellich の定理」 |
| Parseval's identity | Parseval 等式 | `L2C_norm_sq_eq_tsum_coeff_sq` | `‖f‖² = ∑‖f̂(k)‖²` | |
| almost everywhere (a.e.) | ほとんど至る所 | `Filter.Eventually _ (ae μ)`, `∀ᵐ x ∂μ` | 測度ゼロの例外集合を除いて成り立つこと。実変数を明示的に量化する文脈（時刻 $t$、周波数 $\xi$ 等）では「ほとんどすべての $t$」のような言い換えも許容する。house style として「ほとんど至る所」を正式表記とし、「概至る所」は表記揺れとして統一する（issue #67） | 「概至る所」 |
| good representative | 良い代表元 | `GoodRepresentative` | 測度ゼロ同値類の中から良い性質を持つ代表元を選ぶ操作 | |
| convergent subsequence | 収束部分列 | `IsCompact.tendsto_subseq` | コンパクト性から取り出す収束部分列 | |
| diagonal subsequence | 対角部分列 | `StrictMono.comp` | 多段入れ子の収束部分列を一本に合成したもの | |
| energy class | エネルギー類 | `energy_class`, `memH1VF` | `[0,T]` 上で a.e. の $H^1_\sigma$ 所属＋粘性散逸の区間可積分性という正則性クラス。時間可測性フィールドは周囲の $L^2$ 空間へ値を取るため、文字通りの Bochner 空間所属を主張しない（issue #64 / lean-pde issue #146） | 「u ∈ L²(0,T;H¹_σ) という正則性クラス」（文字通りの Bochner 空間所属としての言い換え） |
| proof-carrying type | 証明保持型 | `LerayHopfSolutionFull`, `GalerkinSolutionData` | 数学的性質を型のフィールドとして保持する構造体 | |
| abstract axiom | 抽象公理 | `-- ALLOW_AXIOM:` | 形式化で未証明のまま仮定する命題（`axiom` キーワード） | |
| weak NS equation | 弱 NS 方程式 | `WeakFormNS` | Navier–Stokes の弱形式版（テスト関数との内積形式） | |
| kernel-only | kernel-only | `#print axioms` | `propext/Classical.choice/Quot.sound` のみ公理に依存する状態 | |
| Picard–Lindelöf | Picard–Lindelöf | `galerkin_ode_solution` | 有限次元 ODE の解の存在・一意性定理 | 「Cauchy–Lipschitz」⚠要確認 |
| viscosity coefficient | 粘性係数 | `ν` | Navier–Stokes の粘性項係数 ν > 0 | |
| initial trace | 初期トレース | `initial_cond` | `u(0) = u₀` という初期条件 | |
| compact self-adjoint operator | コンパクト自己随伴作用素 | | ⚠要確認 | |
| Fourier multiplier | Fourier 乗数 | `viscousFormSq`, `stokesTestPairing_R3` | Fourier 空間での乗算として表現される作用素 | |
| tsum convention | tsum 規約 | `tsum` | mathlib では非可算和は +∞ でなく 0 を返す（本形式化の主要罠） | |
| dissipative field | 散逸的（な）場 / 散逸的ベクトル場 | `norm_le_of_forwardSolution_of_dissipative` | すべての $v$ で ⟪v, g(v)⟫ ≤ 0 を満たすベクトル場 | 「消散的」 |
| forward-global solution | 前向き大域解 | `forwardGlobalSolution_exists` | 前向き時刻 t ≥ 0 全体で定義された解。二次場は後ろ向きに爆発しうるため前向きに限る | 「前方大域解」 |
| a priori estimate | アプリオリ評価 | `energy_bound` | 解の存在論に先立って（解であることだけから）導く評価 | 「先験的評価」⚠要確認 |
| Riesz representation | Riesz 表現 | `InnerProductSpace.toDual` | 連続線形汎関数をベクトルとの内積として表す対応。表現するベクトル = Riesz 表現元 | 「リース表現」（カナ単独は非推奨） |
| Galerkin domain | Galerkin 領域 | `Galerkin.Domain` | 幾何に依らず Galerkin 構成を述べるための領域データの束（lean-pde issue #112） | |
| band-limited | 帯域制限（された場） | `viscousEnn_eq_ofReal_of_bandlimited` | ある次数の Fourier 打ち切りで不変な（Fourier 台が有限の）場 | 「バンド制限」 |
| test-shifted convection form | 部分積分形の移流形式 | `TorusConvectionExtension.convValW` | 部分積分で微分をテスト因子へ移した移流形式（略: 部分積分形）。テストの帯域制限のみで総和可能になる | 「移項形式」、「移項移流形式」 |
| Stokes pairing | Stokes 双線形形式 | `stokesTestPairing`, `stokesTestPairing_R3` | 粘性形式の双線形版 $s(u,w)$（$\nu$ 因子は別掲）。対角値 $s(u,u)$ が粘性形式に一致 | 「Stokes テスト対」 |
| lane | 系統 | `exists_lerayHopf_r3` / `exists_lerayHopf_torus3` | ℝ³／トーラス両証明系統を指すリポジトリ内部語。和文散文では「ℝ³ 系統」「トーラス系統」と書く。文脈により「トーラス側／ℝ³ 側」も可（issue #51 の owner 裁定）。数学的な列・級数の意味の「系列」は禁止対象外（lint は lane 固有句のみ検出） | 「レーン」、「トーラス系列」、「ℝ³ 系列」、「両系列」、「本系列」、「旧系列」、「各系列」、「系列側」、「系列ごと」 |
| determined extension / domain | 決定拡張／決定域 | `TorusConvectionExtension.detExtend`, `detDomain` | 片方の因子が帯域制限なら値が一意に決まる拡張構成の局所術語。「決定移流形式」も同系 | |
| equi-Lipschitz | 同程度 Lipschitz 連続 / 同程度 Lipschitz 連続性 | `Bochner.WeakLimitToolkit.cauchySeq_of_equiLipschitz_of_dense` | 同程度連続（equicontinuous）に倣う訳。共通の Lipschitz 定数をもつこと。単独の「同程度 Lipschitz」でなく「連続（性）」まで付す（issue #51 の owner 裁定） | 「等 Lipschitz」 |
