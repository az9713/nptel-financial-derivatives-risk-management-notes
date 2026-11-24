# Independent scientific review: Chapter22

Reviewer: reader_builder_scientific. Disposition: accepted. The reviewer did not author this chapter. Read the complete current manuscript, metadata, all six worked solutions and every line of the laboratory.

## Mathematics and teaching audit

Derived the advance FRA settlement Nδ(L−K)/(1+δL) and checked its date, positive denominator, sign and currency units. The zero-coupon portfolio N units at T1 minus N(1+δK) at T2 has the correct advance value; reinvesting the T1 proceeds at the matching deposit rate also replicates the end-settled linear coupon. Thus equal single-curve values do not assume deterministic realized future fixings. The multi-curve and nonlinear-denominator qualification is essential and is explicitly present.

Recomputed the source forward e^0.06−1=0.0618365465, future scenario advance settlement−0.17295944million and today's distinct value−0.16288707million. Verified the coupon strip telescope before first reset, par-rate weighted average, annuity units and all source/synthetic computations. The synthetic annuity1.875, par5.86666667%, fixed-payer6% value−25000 and coupon-bp sensitivity−1875 are correct and carefully distinguished from a curve DV01.

Independently solved the bootstrap equation, giving P2=0.9056895841 and continuous zero4.95293270%. Checked the full known coupon/remaining discount-horizon distinction for the off-reset floater:1060exp(−0.0225)=1036.41631142; shortening the coupon incorrectly produces1007.08377431. For the receive-fixed source swap, fixed-bond98.23789590 minus floating-bond102.50507175 gives−4.26717585million. The independent coupon-strip calculation retains the known first fixing and reproduces that value. All six solutions have correct direction, dates and units.

The separate-curve floating-leg expression uses payment-date pricing expectations rather than automatically treating arbitrary curve forwards as physical forecasts. Its numerical deterministic counterexample0.06265 versus0.05 is valid, with par6.49222798%. Overnight-compounded observation and advance-fixed term coupons are correctly separated. Checked every comparative-funding gross flow: BBB7.75%, AAAprime−0.25%, dealer0.25%, aggregate0.75% saving conditional on the stated contractual credit and rollover limitations.

## Source passages actually inspected

Read selected actual official normalized captions: position55,500–900seconds (direction, day count, advance settlement/source FRA),995–1200 (post-inception value),1290–1450 (swap strip),1900–2100 (funding terms); position56,1250–1450 (bootstrap) and1620–1800 (floating bond basis); position57,850–1005 (known60 coupon and1060 future bond value),1000–1250 (source receive-fixed swap inputs). This is selected independent verification, not a full second sequential caption read.

Opened Bianchetti's primary Two Curves, One Price presentation and inspected slides5 and8: separate discount/projection curves and payment-date expectations support the chapter's selected claims. Opened the New York Fed administrator methodology and inspected its SOFR Averages and Index paragraphs (business-day compounding, preceding-business-day simple interest over nonbusiness days, actual calendar days/360); the chapter correctly separates that administrator methodology from each swap's contractual observations.

## Executable evidence and boundary

Ran labs/ch22.py in a fresh process; all assertions passed, including bond-versus-strip equality, bootstrap repricing, known first coupon, settlement equivalence, coupon sensitivity, separate-curve failure of telescoping, funding-flow conservation, negative forwards and invalid discount-factor rejection. Checked the displayed numbers independently using the dated formulas above. No unresolved findings remain. Exact manuscript/metadata/lab hashes are in the receipt. No comprehensive audiovisual audit, human certification or completion of separate browser/release gates is implied.
