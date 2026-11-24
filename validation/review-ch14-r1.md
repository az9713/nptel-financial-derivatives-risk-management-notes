# Independent scientific and editorial review: chapter 14

Date: 2026-11-24. Reviewer: scientific_review, a distinct AI reviewer from the chapter author.

Disposition: **accepted** for the exact manuscript, metadata, and laboratory bytes recorded below. No human expert certification or comprehensive audiovisual audit is claimed.

## Scope and results

No-dividend and prepaid-share European bounds, rate-independent discount-factor handling, dividend-reinvestment share count, rate-conditioned no-early-exercise theorem, negative-rate/dividend counterexamples, one-step put continuation, American parity seller superhedges, all six solutions.

Full lab and fresh execution checked; current finite-parameter and nonBoolean integer-step repairs read. Positive-rate call equality and American put parity intervals checked against supplied trees.

The developed explanatory prose, local definitions, assumptions, knowledge order, examples, and all six full solutions were reviewed, as well as the code. Source attribution and source corrections are bounded as follows.

- Position33 seconds273–450: American call waiting rationale and European continuation lower bound.
- Duke option-valuation sections6,9–10: statewise dominance and call bounds, interpreted under the manuscript explicit assumptions.

## Located findings resolved before acceptance

- Medium lab domain: tree_price now requires finite parameters and positive nonBoolean integer step counts, avoiding invalid infinity arithmetic or TypeError from fractional counts.

Remaining findings: none. All six laboratories in this review batch pass default pycodestyle with its standard optional ignores; exact inputs are LF-normalized.

## Original accepted inputs (historical)

- `chapters/ch14.md`: `46fdb38022ee9aaaa2433ed7040523b149ebaf9c4b6005d740d5a67f4cd2536d`
- `chapters/ch14.json`: `e1eec64888e4aa0d4df8c274e17b8bc8e7a66f2c00176e0aa4eb8a211cde994a`
- `labs/ch14.py`: `512f7135cbaf6bfa11845790270efb9ddc09c5aba086026e8155e9cb7de0123b`


## Incremental critical-parity review

Date: 2026-11-24. Reviewer: scientific_review, separate from the author. Accepted for the current inputs below. The full review above describes the earlier edition; its exact bindings are retained in the JSON review history.

Read the complete state-price derivation, its put continuation and exercise context, expanded exercise 5 and solution, and all new lab equations. Independently obtained state prices 100/189 and 80/189, checked cash and stock reproduction, normalized up weight 5/9, European put 320/21, American put 20 and early-exercise premium 100/21. Definitions precede their economic use and the normalized pricing weight is separated from a physical forecast.

Fresh laboratory execution passed. Independent algebra and exact rational checks corroborate the new quantities. pycodestyle passed and the changed source files have canonical LF. This incremental pass did not repeat the earlier full caption or primary-source reading, claim a new full-manuscript review, or inspect browser rendering.

Current accepted inputs:

- `chapters/ch14.md`: `15d397426c2c18b506fba082c0fd3a7fb88407c908373bd3df1738e45cbfdd6a`
- `chapters/ch14.json`: `e1eec64888e4aa0d4df8c274e17b8bc8e7a66f2c00176e0aa4eb8a211cde994a`
- `labs/ch14.py`: `3b711efd978184b787aaf96e64e23960b624258fbaa1168a399cbaf5b0fac26f`

Remaining findings: none within this incremental scope.
