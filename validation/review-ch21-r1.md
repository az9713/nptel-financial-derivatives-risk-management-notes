# Independent scientific review: Chapter21

Reviewer: reader_builder_scientific. Disposition: accepted after complete manuscript, metadata, all six exercise solutions, and full executable lab review. The reviewer did not author this chapter.

## Mathematical and pedagogical audit

Recomputed the signed source delta examples (net minus800 shares; contract multiplication gives80000), the gamma140 hedge (minus200 options and minus180 shares), and the gamma–vega system (400 and6000 options, minus3240 shares). Checked the common-expiry identity Vega=S²στGamma and the resulting rank failure: adding two different strikes does not supply independent common-volatility gamma and vega control. Nearby maturities can be formally invertible yet badly conditioned; the lab explicitly tests the distinction.

Differentiated both spot-dependent peak conditions: gamma peaks at K exp[−(r−q+1.5σ²)τ], vega at K exp[−(r−q−0.5σ²)τ]. Verified the financed PDE identity, gamma–theta relation, and delta-hedged local P&L. The physical variance comparison retains its local-order qualification. Scenario hedge coefficients describe a stipulated joint move rather than an independent factor hedge.

Audited every cash entry in the original quadratic-book example. Book change2371.42857143 plus stock gain1800 gives full wealth4171.42857143. The source's3200 is a closed stock tranche, not the full book result. The quiet-path loss1028.571429 is consistent with financing and time decay. Rebalancing shifts wealth between cash and stock without creating wealth. Checked all six solutions, including the signed scenario hedge, variance threshold, peak formulas, and FX-value delta.

For foreign exchange, differentiated the value of an existing fixed-delivery-price contract rather than a newly quoted forward rate. The correct underlying hedge is Q exp(−rfτ); solving the source's inverse question gives6485372.73143405 pounds. This is distinguished from the quote derivative exp[(rd−rf)τ]. Swap definitions correctly separate advance-fixed term rates from compounded overnight observations and retain the historical benchmark boundary.

## Source evidence actually inspected

Selected actual normalized official captions were read at position51,490–740 seconds; position52,120–400 and730–1000; position53,1450–1730; position54,1000–1250 and1430–1650. These intervals cover the central hedge systems, partial-ledger trap, FX hedge correction and swap introduction. This is selected independent verification, not a full independent reread of all four caption files.

The MIT Kogan stochastic-calculus financing/PDE slides17–20 were inspected during the preceding chapter reviews and supply the financing baseline used here. The FCA primary announcement, https://www.fca.org.uk/news/press-releases/end-libor, was opened and inspected: published1October2024, it states that the final remaining synthetic settings ceased on30September2024 and all35 settings had permanently ceased. The chapter's dated claim is supported.

## Executable verification and acceptance

Ran labs/ch21.py in a fresh process: all assertions passed. Independently checked the quadratic ledger, hedge signs, common-expiry rank constraint, and FX units. The executable full repricing example gives hedge options54.4197029 and57.64410566, stock−11.73504893; nonzero finite-move residuals appropriately remain. The lab covers singular and poorly conditioned hedge systems, scenario versus independent risk cancellation, financing, peak Greeks, and the complete cash ledger.

No unresolved scientific findings remain. Acceptance binds the exact three source digests in the accompanying receipt. It does not certify a comprehensive audiovisual audit, human review, or the separate release/browser gates.
