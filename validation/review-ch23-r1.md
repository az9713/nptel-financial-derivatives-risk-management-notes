# Independent scientific review: Chapter23

Reviewer: reader_builder_scientific. Disposition: accepted. The reviewer did not author this chapter. Read the complete manuscript, metadata, every worked solution and laboratory code.

## Mathematics and pedagogy

Verified domestic-per-foreign conversion V=XBf−Bd and its covered-interest-parity coupon equivalent, including final principals and exclusion of an already-paid initial exchange. Recomputed yen-bond1230.55409740million, dollar-bond9.64385966million, remaining receive-yen value1.54299577million dollars. At100yen/dollar value2.66168132million; inverse-quote derivative−Bf/Y² has the correct sign and units. The chapter makes basis/collateral limitations explicit.

Audited the corrected funding example rather than copying the source's inconsistent principals:20millionAUD at0.5USD/AUD is10millionUSD, not15million. The intermediary's130000USD inflow and220000AUD outflow leave31000 or−13000USD in the stated scenarios; a matching0.55USD/AUD forward locks9000USD. The currencies cannot be added as naked percentage rates. The corrected construction is explicitly original, with its retained currency risk visible.

Checked the lower loss-quantile definition, signs, strict exceedance bound and negative VaR example. With n=500 and confidence99%, ceil(nα)=495 ascending is sixth worst, leaving five strictly greater distinct observations. Historical simulation uses500 shocks from501 levels and retains synchronous factor vectors. Recomputed the paired stock/FX losses120 versus scrambled−2520/2280, illustrating changed dependence without changing marginals.

Re-derived Gaussian VaR with physical drift, annual horizon units and precise normal quantile. Five-day single-asset9830.61401862, rounded-z9846.04706759 and two-asset8387.76654442 are correct. Derived the lag-covariance double-sum count: variance factor9.4672 for five observations withρk=0.4^k, SD ratio1.37602326. The stated Gaussian/independence limitations on quantile scaling and exact GBM bounded-loss formula are correct.

Verified atom-safe ES using partial threshold mass:95%VaR0/ES26;97.5%VaR10/ES46; conditional-on-nonnegative1.3 and conditional-positive32.5 are distinct. Raising extreme loss to1000 leaves95%VaR0 and raises ES206. Checked the convex minimization objective and its one-sided CDF optimality condition, including flat minimizer intervals. For independent4%-chance100 losses, individual VaR0/ES80; sum probabilities0.9216,0.0768,0.0016 give VaR100/ES103.2. All six solutions are correct, with no conflation of pricing and physical scenarios or regulatory inference.

## Source and primary-reference verification

Inspected actual official caption intervals: position58,70–220seconds (funding terms),500–650 (inconsistent cross-currency notionals),840–1040 (yen–dollar swap); position59,270–430 (historical-simulation assumptions),650–880 (gross-shock construction and repricing),1200–1400 and1460–1640 (Gaussian approximation and VaR sign),1840–2050 (time units and source five-day example). These are selected independent passages, not a complete second caption reading.

Opened both Rockafellar–Uryasev primary PDFs. Inspected the general-distribution paper's Definition3 including threshold atoms, Proposition8 finite-scenario formula and Theorem10 minimization/one-sided-slope argument. Read the earlier1999paper's printed pages4–5, which explicitly assume continuous CDFs and give the initial conditional-tail treatment. The chapter's scope and locators match these sources; the atom correction is supported by the general paper rather than silently extending the restricted earlier treatment.

## Laboratory and acceptance

Fresh-process labs/ch23.py execution passed every assertion. It checks currency valuation by two methods, inverse-quote finite difference, complete intermediary residuals, exact-rational empirical quantile indexing, two distinct ES algorithms, dependence pairing, aggregation counterexample, full-precision Gaussian values, covariance-matrix horizon variance, and invalid probability rejection. Scientific inspection independently recomputed all example and solution amounts above. No unresolved findings remain. The receipt binds exact current source bytes; separate browser/release checks and audiovisual limitations remain.
