# Independent scientific review: Chapter24

Reviewer: reader_builder_scientific. Disposition: accepted. The reviewer did not author this chapter. Read the complete manuscript, metadata, all six solutions, source-reading ledger and full laboratory code.

## Mathematical, financial and pedagogical review

Verified signed linear loss mean/covariance, the extra Gaussian assumption required for moment-to-quantile conversion, and the distinction between stock-return and decimal-yield coordinates. The basis-point variance scale10^8 is correct. Recomputed the derivative portfolio variance50400000 and standard deviation7099.295740. Duration's parallel-shift assumptions, signed-dollar sensitivity and continuous-compounding conventions are explicit. The bond example gives daily standard deviation28080 and precise20day90%VaR160934.141192, versus160739.299349 using1.28.

Derived the cash-flow mapping quadratic independently: coefficients2.8e−7,−9.2e−7,5.376e−7. The unique feasible root0.760258938 yields PV49189.321135 and allocations37396.621030/11792.700105. The weighted maturity0.3099353 differs from0.3; matching this interpolated variance and PV does not replicate the original dated payment or every sensitivity. Benchmark return and yield coordinates are distinguished. No exact replication claim is made.

Checked PCA exposure rotation and covariance decomposition, the source six/minus-four example, and the original99.5%-variance counterexample. Direct quadratic-form evaluation gives portfolio variance2000000; the dominant component has zero exposure and therefore retains none of this risk. Standardization changes the model, and uncorrelatedness is correctly distinguished from independence. For the currency forward, verified fixed old domestic payment and signed current domestic-valued legs1491750/−1455000; standard deviation537.152261933 versus1540.197699 with the incorrect same-sign legs. Avoiding double-counted FX risk is explained.

Re-derived the delta–gamma expression and log-coordinate Hessian S²Gamma+SDelta. For centered Gaussian factors, the trace mean and quadratic variance follow from the displayed fourth-moment identity; these moments do not imply a Gaussian loss. The normal-quadrature lab is appropriate for testing fourth moments. Recomputed the short100call plus stock hedge: instantaneous stock-only stress produces loss100[c(S+x)−c(S)−Delta*x], nonnegative by convexity. Exact finite-scenario VaR194.852544/ES361.105115 and gamma198.476274/436.647802 are consistent with sorted tail masses. The full five-year bond loss39929.970007 lies between the displayed first- and second-order estimates, with the nonuniversal-accuracy caveat preserved.

Verified every atomic-tail example by filling only the required threshold mass and independently integrating the finite quantile intervals (ES46). Binomial survival independently computed using scipy.stats.binom.sf(9,250,.01) gives0.0002501900687405077. The expected2.5 exceptions, probability0.0810585162 of zero, clustering counterexample and matching-P&L discussion are correct. The discrete-atom warning avoids treating strict exceedance probability as exactly1−alpha in all laws. All six worked solutions have correct numbers, signs and assumptions.

## Actual source and primary checks

Read selected actual official captions from position60:4–170seconds (covariance),305–500 (duration and assumptions),670–820 (bondVaR),1046–1310 (mapping inputs and interpolated variance),1357–1680 (PCA interpretation and source factor example),1880–2078 (delta/gamma and historical option portfolio),2078–end (currency-forward signs and missing discount details). These selected intervals cover all major lecture mechanisms but are not a complete independent sequential reread.

Opened NIST Properties of Principal Components and inspected its orthogonal-transform, eigenstructure and diagonal-covariance equations. Its standardized/correlation presentation supports the cited eigenstructure; the chapter separately acknowledges covariance versus correlation PCA. Opened the historical BCBS January1996 backtesting PDF and read PDFpages2–6, including static-position hypothetical versus actual trading outcomes, fee effects, independence of exceptions and imperfect statistical power. The chapter labels it historical and does not claim current regulatory compliance. The general Rockafellar–Uryasev Definition3/Proposition8 passages were inspected in Chapter23's independent review and support the scoped atom-aware ES link here.

## Executable evidence and acceptance

Ran labs/ch24.py in a fresh process: all assertions passed, including indefinite-covariance rejection, signed currency legs, source mapping, PCA residual risk, full-versus-Taylor revaluation, atomic tails, Gaussian quadrature, bond curvature and binomial/clustering calculations. Independent calculations above additionally used direct covariance quadratics, explicit quantile integration and scipy's binomial survival implementation. No unresolved scientific findings remain. The receipt binds the exact current manuscript, metadata and lab. It does not certify comprehensive audiovisual inspection, a human review, empirical calibration, or the separate browser/release gates.


## Bounded editorial recheck

Reread the first topic heading and complete curve-shock paragraph after the two agreed repairs. The first timestamp now points to the substantive26second opening rather than the introductory word at4seconds. The curve shocks are described as maturity-specific, preserving their full covariance rather than suggesting statistical independence. Reversing exactly those two edits reproduces the previously accepted manuscript SHA-256; metadata and lab remain byte-identical. The acceptance receipt now binds the repaired current manuscript.
