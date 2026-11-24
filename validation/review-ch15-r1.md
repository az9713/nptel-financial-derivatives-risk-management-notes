# Independent scientific and editorial review: chapter 15

Date: 2026-11-24. Reviewer: scientific_review, a distinct AI reviewer from the chapter author.

Disposition: **accepted** for the exact manuscript, metadata, and laboratory bytes recorded below. No human expert certification or comprehensive audiovisual audit is claimed.

## Scope and results

Full manuscript including previously truncated calendar tail/maturity paragraph; all six worked solutions; signed-payoff/funded-profit framework; interval slopes, attainable roots and infinite tails; covered/protective parity, straddles/strangles/ratios, verticals, equal/unequal-strike butterfly convexity, box financing, and calendar continuation independently checked.

Full laboratory source and fresh execution passed. Synthetic call-data convexity slopes checked independently from strike0 through120. Figure-generating code/data reviewed; this receipt is not a rendered-browser or visual-layout approval.

The developed explanatory prose, local definitions, assumptions, knowledge order, examples, and all six full solutions were reviewed, as well as the code. Source attribution and source corrections are bounded as follows.

- Position36 seconds1178–1360: calendar expiry mismatch and overbroad European maturity claim; manuscript replaces the latter with an explicit dividend counterexample.
- Duke stock-plus-option strategy descriptions; OIC long-straddle Description/MaxLoss/MaxGain/Breakeven and long-call-butterfly Description/Profit-Loss passages independently inspected.

## Located findings resolved before acceptance

No unresolved scientific, editorial, or numerical findings were identified in this review.

Remaining findings: none. All six laboratories in this review batch pass default pycodestyle with its standard optional ignores; exact inputs are LF-normalized.

## Original accepted inputs (historical)

- `chapters/ch15.md`: `bdb2df2b6b59f83c6b8ba1bb9e38b3987a6bc6bb03c5d6c224f69e2178857582`
- `chapters/ch15.json`: `8aa3ab0413eaca6e6250e800b085ea66be19307d2d16f193152b1fdf1d0c750a`
- `labs/ch15.py`: `c763e07f0e57abe6e0bd97b08fd97c80582d741c231e3022b1e9ad95445e726a`


## Incremental critical-parity review

Date: 2026-11-24. Reviewer: scientific_review, separate from the author. Accepted for the current inputs below. The full review above describes the earlier edition; its exact bindings are retained in the JSON review history.

Read the full unequal-strike piecewise construction and its preceding convexity/normalization context, expanded exercise 5 and solution, the new numerical precision paragraph, and full current Portfolio implementation with all new regressions. Exact rational arithmetic confirms weights (2/3,-1,1/3), debit 2, peak 20/3, maximum profit 14/3 and roots 93 and 114. The naive (1,-2,1) tail is -10. A reproducible small-slope classification defect was reported to the author and repaired before this acceptance; see resolved finding.

Fresh laboratory execution passed. Independent algebra and exact rational checks corroborate the new quantities. pycodestyle passed and the changed source files have canonical LF. This incremental pass did not repeat the earlier full caption or primary-source reading, claim a new full-manuscript review, or inspect browser rendering.

Resolved finding: Medium: labs/ch15.py affine classification used an absolute zero tolerance, causing Portfolio(stock=1e-14) to report an entire zero-profit interval and omit its isolated root 100. Author now classifies exact zero slopes/values exactly, keeps numeric tolerances separate, and tests tiny stock/call positions. Current implementation and fresh execution independently rechecked.

Current accepted inputs:

- `chapters/ch15.md`: `5d577869e85ed1ac235ddc37f52db62fd991cef0eba4d3a0f3071ac81c979a5f`
- `chapters/ch15.json`: `8aa3ab0413eaca6e6250e800b085ea66be19307d2d16f193152b1fdf1d0c750a`
- `labs/ch15.py`: `0efba05efcadf763792574a9fe1562b89032a4ac2fd622b9858ad02f616585c3`

Remaining findings: none within this incremental scope.
