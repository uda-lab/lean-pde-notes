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
| divergence-free | 発散ゼロ | `L2Sigma`, `L2Sigma_R3` | 「ソレノイダル (solenoidal)」とも。T³ では div ⊂ Fourier 核の交叉として定義 | 「発散なし」「無発散」 |
| mollifier | 軟化子 | `TimeConvolution` | C^∞ コンパクト台の近似恒等核 | 「正則化核」⚠要確認 |
| Galerkin approximation | Galerkin 近似 | `GalerkinSolutionData`, `GalerkinSolutionData_R3` | 有限次元 ODE 族による近似手順 | 「ガレルキン近似」（カナ表記可・英字と統一を推奨） |
| Galerkin scheme | Galerkin スキーム | `R3GalerkinScheme`, `velocityProjection_n` | 近似射影族の束 | |
| weak convergence | 弱収束 | `tendsto_nhdsWithin_atTop` | Hilbert 空間での弱位相での収束 | 「弱い収束」 |
| strong convergence | 強収束 | | L² ノルム収束 | 「強い収束」 |
| weak-* convergence | 弱\*収束 | | 双対空間での弱\*位相での収束 ⚠要確認 | |
| compact embedding | コンパクト埋め込み | `rellich_seq_compact`, `rellich_L2Sigma` | `H¹ ↪ L²` の Rellich–Kondrachov 埋め込み | 「コンパクト的埋め込み」 |
| precompact | 前コンパクト | `H1_ball_totallyBounded` | 閉包がコンパクト。本形式化では「全有界 (totally bounded)」として扱う | 「相対コンパクト」⚠要確認 |
| totally bounded | 全有界 | `Metric.totallyBounded_iff` | 任意の ε>0 に対し有限 ε-網をもつ | |
| compact operator | コンパクト作用素 | `isCompactOperator_of_locallyCompactSpace_dom` | 有界集合をコンパクトな像へ送る作用素 | 「コンパクト型作用素」 |
| compact support | コンパクト台 | `tsupport ψ ⊆ Set.Ioo 0 T` | 関数が零でない集合の閉包がコンパクト | 「有界台」⚠要確認 |
| orthogonal projection | 直交射影 | `orthogonalProjectionOnto`, `HasOrthogonalProjection` | 閉部分空間への直交射影作用素 | 「直交投影」 |
| Leray projection | Leray 射影 | `lerayProjection`, `lerayProjection_R3` | `L²` 上の発散ゼロ部分空間への直交射影 | |
| Hilbert space | Hilbert 空間 / ヒルベルト空間 | `InnerProductSpace`, `CompleteSpace` | 内積完備空間。略称 H | 「ヒルベルト空間」（カナ・英字どちらも可） |
| Sobolev space | Sobolev 空間 / ソボレフ空間 | `h1EnergySq`, `memH1VF_R3` | `H^s` または `W^{k,p}`。本形式化では H¹ が主役 | 「ソボレフ空間」（カナ可） |
| dissipative evolution | 散逸発展 | `DissipativeEvolution` | `H + reg + viscousForm + convForm + isTest` の抽象束 | |
| pivot Hilbert space | ピボット Hilbert 空間 | `DissipativeEvolution.H` | Gelfand 三つ組の中間 H | |
| Gelfand triple | Gelfand 三つ組 | | `V ↪ H ↪ V'`。本形式化では採用しない（`reg` で代替） | 「ゲルファント三つ組」 |
| regularity functional | 正則性汎関数 | `DissipativeEvolution.reg`, `h1EnergySq`, `viscousFormSq` | `reg(u)` のレベル集合コンパクト性 ⇒ Rellich | |
| viscous form | 粘性形式 | `viscousFormSq`, `stokesTestPairing_R3` | Stokes 双線形形式 `ν∫∇u:∇v` | |
| convection form | 移流形式 | `convForm`, `convIntegralSchwartz`, `galerkinConvection` | `b(u,v,w) = ∫(u·∇)v·w`（反対称 `b(u,v,w) = −b(u,w,v)`） | |
| weak formulation | 弱形式 | `WeakFormNS` | Navier–Stokes 方程式の弱積分形式 | 「弱い定式化」 |
| test function | テスト関数 | `DissipativeEvolution.isTest`, `IsSchwartzDivFree_R3` | 弱形式で積分のパートナーとなる滑らかな関数 | 「試験関数」⚠要確認 |
| Schwartz function | Schwartz 関数 | `SchwartzMap`, `𝓢(ℝ³,ℝ)` | 急減少滑らか関数。ℝ³ の弱発散定義に使用 | |
| weak divergence | 弱発散 | `divTestFunctional`, `L2Sigma_R3` | 超関数的発散ゼロ：`∀φ∈𝓢, ∫u·∇φ=0` | |
| Fourier coefficient | Fourier 係数 | `mFourierCoeff3` | 本形式化では T³ の離散 Fourier 係数を直接使用 | |
| Fourier truncation | Fourier 截断 | `fourierProjection`, `velocityProjection_n` | 箱領域内のモードのみ保持する有限次元射影 | |
| limit passage | 極限移行 | `galerkin_limit_passage`, `galerkin_limit_passage_R3` | Galerkin 近似の極限で非線形項を移行する操作 | 「極限の移行」 |
| Aubin–Lions lemma | Aubin–Lions 補題 | `aubin_lions`, `aubin_lions_R3` | 時間コンパクト性：`L²(0,T;V)∩W^{1,q}(0,T;V') ↪ L²(0,T;H)` がコンパクト | |
| Rellich–Kondrachov theorem | Rellich–Kondrachov 定理 | `rellich_seq_compact` | `H¹(T³) ↪ L²(T³)` がコンパクトである定理 | 「Rellich の定理」 |
| Parseval's identity | Parseval 等式 | `L2C_norm_sq_eq_tsum_coeff_sq` | `‖f‖² = ∑‖f̂(k)‖²` | |
| good representative | 良い代表元 | `GoodRepresentative` | 測度ゼロ同値類の中から良い性質を持つ代表元を選ぶ操作 | |
| convergent subsequence | 収束部分列 | `IsCompact.tendsto_subseq` | コンパクト性から取り出す収束部分列 | |
| diagonal subsequence | 対角部分列 | `StrictMono.comp` | 多段入れ子の収束部分列を一本に合成したもの | |
| energy class | エネルギー類 | `energy_class`, `memH1VF` | `u ∈ L²(0,T;H¹_σ)` という正則性クラス | |
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
