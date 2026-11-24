# Independent scientific and editorial review: Chapter 05

## Verdict

Accepted after the complete notation repair, at the exact current manuscript, metadata, and laboratory digests in the companion receipt. The reviewer did not author the chapter. The full manuscript, all six solutions, metadata, and code were read. The laboratory was executed before and after the repair; its completed numerical certificates agree. All changed display equations, exercise statements, and solution products were inspected before acceptance.

## Repaired clarity finding

The first draft reused n for a signed short-contract count after Chapter03 used n for signed long contracts. An explicit warning prevented a hidden sign error, but the switch weakened book-wide notation. The author changed the hedge-sizing position to n_s and its optimum to n_{s,*}, preserving n for signed-long positions. A first repair missed several implicit TeX products; these were located and corrected before final acceptance. The code's documented return convention and variable names now match. The variance derivation and all numerical results are unchanged. No finding remains.

## Mathematical and numerical checks

The variance quadratic, positive second derivative, and completed-square proof establish the unique real optimum under finite moments and positive futures variance. The hedge-ratio units are B units per A unit, and the multiplier converts the required B quantity to contracts. Negative covariance reverses the required position. The completed-square identity correctly gives a squared-correlation variance reduction rather than a correlation percentage.

For the synthetic processor, covariance4, futures variance6.25, hedge ratio0.64, and target quantity147200 give5.888 short contracts. Six is the nearest integer. The residual variance76176000000 and exact rounding penalty49000000 give76225000000; the continuous residual standard deviation is276000. These quantities were independently checked as well as reproduced by the lab.

The cross-hedge identity distinguishes the futures-underlying basis from the relative spot spread and states its unit restriction. The changed-relationship example has training hedged variance1, new unhedged variance1.1, and stale-hedge variance3.5. This correctly shows a failure of parameter stability without contradicting a theorem optimized for the original covariance. All six solutions develop the mechanism and applicable boundary.

## Source and prose scope

Selected official cues in position12 around1130–1246seconds were checked for the quantity and decision-horizon setup, and position13 around678–831seconds for the variance substitution and perfect-correlation condition. NIST's linear least-squares page was retrieved independently; its fitting definition, extrapolation caution, and outlier sensitivity support the adjacent paragraph. Full sequential source reading by the author is recorded separately.

The chapter is narrower than the opening pilot but supplies the required derivation, interpretation, worked sizing, integer certificate, estimation counterexample, and full solutions. Its concise sections do not substitute a bare formula list for reasoning. This review covers the full scientific/editorial chapter and code with bounded source verification, not a complete second transcript or audiovisual audit. The first independent review and reader/release checks remain separate gates. No human expert or formal certification is claimed.

## Listing-format recheck

The final PEP8/79-column laboratory was read in full after formatting and executed again. The reviewed mathematical expressions and certificate outputs remain consistent. The current lab digest is rebound in the receipt; manuscript and metadata bindings are unchanged. This bounded code recheck does not imply another full source audit.

Final canonical-line-ending recheck: the lead reviewer independently reconstructed the prior CRLF bytes from the LF version and matched the previous accepted SHA-256 for every changed bound file. Laboratory ASTs also match. This newline-only operation changes no scientific text or code behavior; the receipt now binds the canonical LF bytes. Evidence: `validation/line-ending-normalization.json`.
