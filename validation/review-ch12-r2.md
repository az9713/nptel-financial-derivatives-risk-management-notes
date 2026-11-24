# Independent scientific and editorial review — Chapter 12

Reviewer source_research; independent of reader_builder. Full manuscript, metadata, all six solutions and complete lab source read. Fresh laboratory execution passed.

Checked every invoice and conversion unit: the per100 clean component is multiplied by CF, accrued interest is separately added, and contract face supplies the final1000 scale. Coupon-aligned and quarter-off-cycle six-percent normalization calculations were independently traced; the quarter factor sqrt(1.03) and clean-interest subtraction are correct under the stated teaching convention. Dirty spot, dated coupon removal, delivery AI subtraction and CF division reverse consistently. CTD ranking uses acquisition less invoice, not the smallest cash price. The revised futures DV01 carries current cash sensitivity to delivery before dividing by CF. The36-short hedge explicitly uses A=1, and the A=1.02 case checks the carried sensitivity. See the subsequent correction record below.

Independently opened all three cited official CME pages: conversion calculation introduction/Exhibit1 verifies six-percent normalization and product-dependent maturity rounding; conversion look-up paragraph verifies the separate AI invoice; delivery-process and NoticeDay paragraphs verify short-side selection and eligible-security choice. No complete official factor algorithm or current basket is claimed. The complete-caption author ledger was inspected; this is not a repeat full-caption or audiovisual audit.

Fresh lab reproduced CF1.462295439 and1.219862025, CTD costs800/200/400, dirtyforward102.050587522 and normalized111.722875024. Finite-difference checks of periodic-yield duration pass. All worked solutions and example arithmetic agree. No remaining findings; exact current files accepted.

## Subsequent independent repair recheck

Subsequent independent r1 review identified a genuine omitted multiplicative carry factor in the original cash-DV01 shortcut. I initially missed that issue. Re-read revised section6, exercise5/solution5 and the complete changed lab. Differentiating F=[A(Bcash-J)-AI]/CF with frozen A,J,AI,CF gives DF=A Dcash/CF. The36-contract case now explicitly assumes A=1; A=1.02 gives85 dollarDV01 and35.29411765contracts. Central finite difference independently checks that formula. Integer/nonbool period and finite rate/coupon guards/regressions are correct; fresh full lab passed.
