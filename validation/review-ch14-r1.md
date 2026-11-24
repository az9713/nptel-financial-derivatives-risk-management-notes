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

## Exact accepted inputs

- `chapters/ch14.md`: `46fdb38022ee9aaaa2433ed7040523b149ebaf9c4b6005d740d5a67f4cd2536d`
- `chapters/ch14.json`: `e1eec64888e4aa0d4df8c274e17b8bc8e7a66f2c00176e0aa4eb8a211cde994a`
- `labs/ch14.py`: `512f7135cbaf6bfa11845790270efb9ddc09c5aba086026e8155e9cb7de0123b`
