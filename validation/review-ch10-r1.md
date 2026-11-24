# Independent scientific and editorial review: chapter 10

Date: 2026-11-24. Reviewer: scientific_review, a distinct AI reviewer from the chapter author.

Disposition: **accepted** for the exact manuscript, metadata, and laboratory bytes recorded below. No human expert certification or comprehensive audiovisual audit is claimed.

## Scope and results

Discount-price and investment-yield transformations; positive-price and positive-accrual domains; 25-dollar DV01 and 2500-dollar quote-point scale; forward zero-bond replication; all six financed/date/sign solutions.

Fresh standard-library lab execution and independent rational forward-price check. Positive computed quotation price and zero-accrual yield regressions were read after repair.

The developed explanatory prose, local definitions, assumptions, knowledge order, examples, and all six full solutions were reviewed, as well as the code. Source attribution and source corrections are bounded as follows.

- Playlist position24 seconds1240–1450: discount versus cash-investment denominator and historical quotation scale.
- TreasuryDirect Understanding Pricing, Bills section: face-based discount and360-day basis.

## Located findings resolved before acceptance

- Medium: quote_price could return nonpositive cash prices. Author now rejects those outputs and tests zero/negative price cases.
- Medium: annualized investment_rate accepted zero accrual. Author now rejects it, while preserving legitimate zero-day bill redemption.

Remaining findings: none. All six laboratories in this review batch pass default pycodestyle with its standard optional ignores; exact inputs are LF-normalized.

## Original accepted inputs (historical)

- `chapters/ch10.md`: `5c422782ed73cd4d27ed021f9054381a37a7e0881b9f5b32abdb74d4c5fd8bf8`
- `chapters/ch10.json`: `16d9fba6a1365a8bbd0c4939e2eb179f8a2e094caa051c6e86be1034902e5394`
- `labs/ch10.py`: `07e40361487745bf5b85e2ec4735e4655e88aa95aaf5435f35107f6914663079`


## Incremental critical-parity review

Date: 2026-11-24. Reviewer: scientific_review, separate from the author. Accepted for the current inputs below. The full review above describes the earlier edition; its exact bindings are retained in the JSON review history.

Read the added investment-yield-coordinate derivation, surrounding quotation/sensitivity context, expanded exercise 2 and solution, and every changed lab statement. Independently differentiated r_s = d/(1-d alpha), recovered the discount-price derivative by the chain rule, and checked 24.37890625 per investment-yield basis point and 25 per discount-yield basis point. Finite translated shocks represent the same price change rather than equal numerical yield shocks.

Fresh laboratory execution passed. Independent algebra and exact rational checks corroborate the new quantities. pycodestyle passed and the changed source files have canonical LF. This incremental pass did not repeat the earlier full caption or primary-source reading, claim a new full-manuscript review, or inspect browser rendering.

Current accepted inputs:

- `chapters/ch10.md`: `b0d505c63b3939b6b0b832fe869acd17b930f4042e2d32d6f114e3052c88a520`
- `chapters/ch10.json`: `16d9fba6a1365a8bbd0c4939e2eb179f8a2e094caa051c6e86be1034902e5394`
- `labs/ch10.py`: `1d4b0fa6d4edd795aa74a70fe4c1b7cd16c9a4f359bce3fa81f919ac28756544`

Remaining findings: none within this incremental scope.
