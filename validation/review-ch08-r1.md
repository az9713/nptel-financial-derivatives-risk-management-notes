# Independent scientific review: chapter 08

Accepted at the exact manuscript, metadata, and laboratory digests in the accompanying receipt. The reviewer did not author this chapter. The complete text, all derivations and examples, six full exercise solutions, metadata, and code were read. The lab passed in a fresh process. No unresolved finding remains.

Discount factors are correctly defined by currency, credit/funding setting, payment date, and compounding convention. Positive discount factors need not be at most one. Coupon valuation follows dated-claim replication. The forward lending stream, ratio of discount factors, simple versus continuous quotations, and sequential bootstrap all use the correct signs and dates. The forward is not presented as an unconditional expected future spot rate.

The annual positive-cash-flow yield inverse has the stated monotonicity, endpoint limits, and uniqueness. Its position between aligned spot-rate extrema follows positive-term dominance. The par-coupon, zero, and annuity examples use the same curve and appropriately different payment patterns. The one-price/many-curves construction preserves the exact price and hence unique stream-specific YTM. Portfolio YTM is correctly obtained by aggregating payments, not averaging individual yields with incompatible maturity patterns.

The algebraic YTM definition is carefully separated from its reinvested-terminal-wealth interpretation. The proof placing maturity growth between reinvestment rate and YTM is valid for positive cash flows and the specified common terminal horizon. Early sale introduces a new market-price term and invalidates that interval proof. The lower-YTM/higher-growth reinvestment example is internally consistent, and the discount-bill face denominator and360day basis are distinguished from a365day compounded equivalent.

Selected actual captions inspected: position20 at130–650seconds (definition and three bond patterns) and1260–1540seconds (curve nonuniqueness and coupon/yield order); position21 at50–365seconds (reinvestment interpretation) and1500–1760seconds (bill convention). The cited MIT fixed-income PDF slides19–34 were opened locally, directly supporting the dated forward transaction and coupon-as-zero portfolio claims. TreasuryDirect's pricing explanation was retrieved directly and confirms the bill price/discount quotation relationship. Mathematical qualifications and proofs are the chapter's explicit reconstructions, not uncritically copied source claims.

Every worked solution and numerical value was independently checked. The complete code uses a monotone bracketed search with an explicit lower-bracket rejection, reprices positive flows, preserves an alternative curve's exact price, and verifies reinvestment bounds and rank reversal. Fresh output gives par coupon146.439628, annuity600.515996, annuity yield0.131324, year-two forward0.202273, portfolio yield0.112891, and reinvestment growth0.071934 versus0.068023. The bill equivalent0.063047 agrees with the stated formula.

The chapter explains why dated prices precede quoted yields and uses counterexamples exactly where common interpretations fail. Units, horizons, and definitions precede use; all six solutions are reconstructible. This complete authored-chapter/code review includes selected actual captions and primary references, not an independent reread of every caption cue or a comprehensive audiovisual audit. No human expert certification, formal proof verification, or replacement of package/browser gates is implied.


## Bounded LF normalization recheck

Reconstructed the former CRLF bytes from each affected canonical LF file and matched its previously accepted SHA-256 exactly. All unaffected inputs retain their accepted digests. The Python AST is identical and the chapter lab passed a fresh execution. This rebind changes byte-level acceptance only; the full scientific review above remains applicable. Evidence: `validation/line-ending-normalization.json`.
