# Independent scientific/editorial review: Chapter 01

Date: November 24, 2026. Reviewer: scientific_review (AI reviewer, separate from the chapter author).

## Verdict

Accepted at the current manuscript, metadata, and laboratory hashes in the companion JSON receipt. Three small issues found during the first pass were repaired and independently rechecked. The chapter's mathematics, signs, units, cash-flow timing, examples, and all six solutions are correct in the stated finite constructions. The running importer case develops the distinctions between payoff and financed profit, a terminal hedge and interim liquidity, and equal moments and statewise replication. The repaired definitions now introduce central clearing and short selling before their technical use. The law-of-one-price proof states its usable-proceeds and zero-fee assumptions. Generator and empty-scenario input behavior is tested. No unresolved scientific, pedagogical, or code defect remains in this review scope.

## Findings repaired and independently rechecked

### R1 — Define central clearing before using it as an explanatory mechanism

Location: `chapters/ch01.md:63`. The phrase “normally with central clearing” assumes a finance-specific mechanism not yet defined. The later risk paragraph explains its consequences but not explicitly who replaces the original counterparties. This fails the local-definition part of the chapter contract.

Replace the opening paragraph of section 4 with:

> A **futures contract** is a standardized contract traded under an exchange's rules, normally with central clearing and periodic settlement of gains and losses. **Central clearing** places a central counterparty between the original trading parties: it takes the buyer's side against a seller and the seller's side against a buyer. The participants then face that central counterparty under its rules rather than relying solely on each other's performance. Standardization specifies features such as the reference asset, contract quantity, maturity, delivery or cash-settlement mechanism, and quotation units. Standardization can support liquidity, but it does not guarantee that every contract can be traded in any quantity at an unchanged price.

Source check: [CPSS–IOSCO Principles for Financial Market Infrastructures](https://www.bis.org/publications/principles-financial-market-infrastructures.pdf), paragraph 1.13, printed p. 9. The chapter's existing qualification that clearing mitigates rather than eliminates risk must remain.

### R2 — Give the short-sale cash-flow contract used by the proof

Location: `chapters/ch01.md:128–130`. “Short selling” and “short A” are used without defining the received initial proceeds and the resulting future obligation. This makes the crucial law-of-one-price construction depend on an unintroduced market operation.

Insert immediately after the opening paragraph of section 7:

> To **sell a claim short** in this one-period model means receiving its executable sale price now while taking the obligation to deliver its specified payoff at maturity. For an ordinary security this can require borrowing it and returning it later. We assume that the short position is permitted, its proceeds can be used, and its borrowing fees and collateral costs are zero. These assumptions are needed for the following cash-flow construction.

The next paragraph can then retain its existing proof. This is a model definition, not a universal claim that real short-sale proceeds are unrestricted or borrowing is free.

### R3 — Preserve a single-use iterable before validating scenarios

Location: `labs/ch01.py:5–17`. `values = [*rates, ...]` consumes a generator. Later comprehensions then return three empty outputs without an exception. Reproduction: `costs((x for x in [80, 86, 92]), 100000, 86, 2)` produces `([], [], [])` instead of the chapter's cost vectors.

Replace the function's opening with:

```python
def costs(rates, quantity, delivery, premium, growth=1.0):
    """Return costs for a nonempty finite iterable of exchange-rate scenarios."""
    rates = list(rates)
    if not rates:
        raise ValueError("Need at least one exchange-rate scenario")
    values = [*rates, quantity, delivery, premium, growth]
```

Retain the remaining domain checks and formulas. Add a check that a generator produces the same vectors as the corresponding list and that an empty iterable is rejected. This verifies actual API behavior without mirroring the finance calculation.

## Minor clarity correction

`labs/ch01.py:1` says “no I/O effects”, but the executable script prints its results. Replace the module description with “Finite cash-flow certificates; no filesystem, network, or trading effects.” Console output is intentional and useful.

## Validation performed

- Read `chapters/ch01.md`, `chapters/ch01.json`, and `labs/ch01.py` in full, including all exercises and complete solutions.
- Read the full normalized English NPTEL Official caption track for the overview recording sequentially. The linked topic locators correspond to the derivative definition, uses, forwards, futures, options, swaps, and arbitrage passages. The disclosed relocation of the expanded arbitrage discussion is pedagogically justified and does not misattribute original constructions.
- Executed `python labs/ch01.py`: all assertions passed and printed vectors match the chapter.
- Independently verified invoice, option-cost, partial-hedge, swap, payoff-moment, and margin-ledger numbers, including exact rational arithmetic where applicable.
- Retrieved the relevant [CME margin explanation](https://www.cmegroup.com/education/courses/introduction-to-futures/margin-know-what-is-needed), [OIC option-rights description](https://www.optionseducation.org/optionsoverview/options-basics), and PFMI overview/definition passages. The cited margin, option obligation, and residual credit/liquidity qualifications are supported. PFMI Principles 4, 6, and 7 appear together on printed p. 1; paragraph 1.13 supplies the central-counterparty definition.

## Structural and prose assessment

The chapter sustains one consequential business case rather than offering disconnected definitions. Equations have defined variables, financial interpretations, and worked checks. The no-arbitrage proof correctly requires feasible trading and identical statewise payoffs; it does not claim that equal expected return and variance imply arbitrage. The option example correctly distinguishes premium, payoff, and financed profit. The futures ledger properly exposes liquidity demands despite terminal cancellation. The solutions are solvable from the chapter and show their reasoning.

No word-count or citation-count quota was used to establish quality. No visual figure is needed for this pilot's argument: the dated payoff table and explicit cash-flow ledgers carry the relevant comparisons. The text avoids hype and source narration in its scientific body; the source and production scope stays in the final note.

## Limits

This review does not certify other chapters, the full playlist, browser rendering, publication, accessibility, or a comprehensive audiovisual source audit. It is independent AI review, not human expert certification or formal proof verification. The acceptance receipt binds the repaired Markdown, metadata, and laboratory files. Any subsequent material change requires an updated review binding.

## Final recheck

The repaired laboratory was executed again successfully. Generator inputs produce the list result, empty scenarios raise ValueError, and every source listing line is at most 79 characters. The effects description correctly excludes filesystem, network, and trading effects while retaining deliberate console output. The current scientific text has the required first-use definitions and short-sale assumptions.


## Incremental critical-parity review

Date: 2026-11-24. Reviewer: scientific_review, separate from the author. Accepted for the current inputs below. The full review above describes the earlier edition; its exact bindings are retained in the JSON review history.

Read the complete added funding-reserve subsection and its surrounding settlement/financing context, the revised laboratory interpretation, and the complete funding_reserve implementation and regressions. Independently derived the discounted recurrence and positive-reserve and zero-reserve necessity branches. Exact rational arithmetic gives minimum reserve 60000000/101 and zero-reserve terminal balance -60 for the three settlements at account factors (1.01)^i. The finite scenario maximum and asymmetric funding limitations are explicit.

Fresh laboratory execution passed. Independent algebra and exact rational checks corroborate the new quantities. pycodestyle passed and the changed source files have canonical LF. This incremental pass did not repeat the earlier full caption or primary-source reading, claim a new full-manuscript review, or inspect browser rendering.

Current accepted inputs:

- `chapters/ch01.md`: `70ce44eabbab8d704685c5ea25ddd21c29bfef10a302bf697c69842aabfef81e`
- `chapters/ch01.json`: `37e805a3bfd47f4d1d0e3a20f9f02381180766a3fc225d0d3f2fe41edbcdbd2d`
- `labs/ch01.py`: `46854b4eecd4f54e977a19ef232db9738a761064338a28519923a37328727552`

Remaining findings: none within this incremental scope.
