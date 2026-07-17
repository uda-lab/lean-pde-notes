# Bibliography — leray-hopf-notes 引用文献

corpus の `statement_ja` / `proof_ja` / `gap.note` が略記で引く一次・標準文献の正典。
各エントリは machine-parseable な `### \`citation-id\`` 見出しを持つ（`scripts/bibliography.py`
がこの見出しをパースして corpus の `references[].id` を検証し、site 表示用データを生成する）。

**使い方（corpus 側）**: 宣言の主張・証明・命名/定義選択が特定文献に基づく場合、その corpus
YAML に `references:` フィールドを追加する。

```yaml
references:
  - id: temam2001
    locator: "III.3"    # 章・定理・ページ等のピンポイント locator（任意）
```

`id` は本ファイルの見出しと一致していなければならない（`scripts/validate.py` が検証する）。

新しい文献を追う場合は、下の一次文献セクションに `### \`new-id\`` 見出しで追記すること。
`id` は `^[a-z][a-z0-9-]*$`（小文字英数字とハイフン、先頭は英字）。

---

## 一次文献（corpus が略記で引くもの）

### `leray1934`

Leray, J. (1934). "Sur le mouvement d'un liquide visqueux emplissant l'espace." *Acta
Mathematica*, 63, 193–248.
[doi:10.1007/BF02547354](https://doi.org/10.1007/BF02547354)

弱解の存在証明の起源（3次元 Navier–Stokes、全空間 $\mathbb{R}^3$）。本コーパスでは
「無条件の局所 Rellich 定理」等の文脈で引かれる。

### `temam2001`

Temam, R. (2001). *Navier-Stokes Equations: Theory and Numerical Analysis*. Reprint of
the 1984 edition. AMS Chelsea Publishing, Providence, RI. ISBN 0-8218-2737-5.
(Originally published: North-Holland, 1977; revised editions 1979, 1984.)

corpus の「Temam III.3」「Temam II.§1」等は本書の章番号を指す（AMS Chelsea 2001 版の
章構成は 1984 版と同一）。

### `lemarie-rieusset2002`

Lemarié-Rieusset, P.G. (2002). *Recent Developments in the Navier-Stokes Problem*.
Chapman & Hall/CRC Research Notes in Mathematics 431. Chapman & Hall/CRC.
ISBN 1-58488-220-4.

corpus の「Lemarié-Rieusset §6」は本書の節番号を指す。

### `rrs2016`

Robinson, J.C., Rodrigo, J.L., Sadowski, W. (2016). *The Three-Dimensional
Navier–Stokes Equations: Classical Theory*. Cambridge Studies in Advanced
Mathematics 157. Cambridge University Press. ISBN 978-1-107-01966-9.

**略称 `RRS`** は著者三名（**R**obinson, **R**odrigo, **S**adowski）の頭文字。corpus の
「RRS §3.2」は本書の節番号を指す。

---

## 補助文献（本コーパスが繰り返し依拠する標準定理・不等式）

corpus 中で "Rellich"、"Aubin–Lions"、"Ladyzhenskaya の不等式" 等の名称のみで言及される
標準結果の出典。個々の corpus エントリすべてに `references:` を付す網羅的な対応付けは本
issue #68 の一次スコープ外（対象は上の一次文献の未解決略記の解消）だが、代表的な出典を
ここに記録しておく。

### `simon1986`

Simon, J. (1986). "Compact sets in the space $L^p(0,T;B)$." *Annali di Matematica Pura
ed Applicata*, 146, 65–96.
[doi:10.1007/BF01762360](https://doi.org/10.1007/BF01762360)

いわゆる Aubin–Lions（–Simon）補題の標準的な現代形。corpus の `aubin_lions` /
`aubin_lions_R3` 系列が使う時間コンパクト性はこの形。

### `ladyzhenskaya1969`

Ladyzhenskaya, O.A. (1969). *The Mathematical Theory of Viscous Incompressible Flow*
(2nd revised ed., translated from the Russian by R.A. Silverman). Mathematics and its
Applications. Gordon and Breach.

corpus の "Ladyzhenskaya の不等式" 等の言及の出典。

### `nirenberg1959`

Nirenberg, L. (1959). "On elliptic partial differential equations." *Annali della
Scuola Normale Superiore di Pisa*, Classe di Scienze, Ser. 3, 13(2), 115–162.

Gagliardo–Nirenberg 補間不等式の標準出典（Gagliardo の独立な同時期の結果と合わせて
「Gagliardo–Nirenberg」と呼ばれる）。

### `evans2010`

Evans, L.C. (2010). *Partial Differential Equations* (2nd ed.). Graduate Studies in
Mathematics 19. American Mathematical Society. ISBN 978-0-8218-4974-3.

corpus が引く Rellich–Kondrachov コンパクト埋め込み定理（§5.7 "Compactness", Theorem 1,
p. 286 — 目次と本文で確認済み）および Grönwall の不等式（§B.2、本文中の引用表記と同一）
の教科書的出典。原論文（Rellich 1930,
Kondrachov 1938, Grönwall 1919）ではなく標準教科書を挙げているのは、本コーパスの
文脈での引用がいずれも「この定理の現代的な標準形」を指しており、原論文の historically
exact な主張とは形が異なるため。
