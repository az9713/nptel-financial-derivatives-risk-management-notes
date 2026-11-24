# Independent scientific review: chapter 07

Accepted at the exact manuscript/metadata/lab digests in the accompanying receipt after localized arithmetic repairs. The reviewer did not author this chapter. All prose, formulas, numerical cases, six full solutions, metadata, and code were read. The laboratory passed in a fresh process before and after repair. No unresolved finding remains.

The stock-portfolio denominator and notional-normalized futures change correctly avoid dividing by a futures contract's zero initial value. Covariance linearity yields the target-beta formula including a nonunit futures beta. Signed-long counts, notional units, beta reduction/increase, fractional counts, and rounding residuals are consistent. Beta neutrality is properly distinguished from minimum total variance, and the general residual formula retains futures tracking error and covariance with stock residuals.

The carry construction reinvests share quantities under an explicit proportional dividend model, distinguishes forward-style terminal replication from actual futures funding, and keeps remaining maturity at early hedge closure. Historical250-multiplier illustrations are not treated as current product specifications. The source20,000-share attribution correctly separates a realized residual from expected alpha; CAPM is not misapplied as a statewise return equation. The six-contract example explicitly corrects the source's spoken ten-contract slip while preserving its underlying data. Frictional upper and lower restrictions follow feasible trades with the correct bid/ask and borrowing/lending sides; they are stated as restrictions from those trades rather than an unconditional single fair price.

All six worked solutions were independently checked. Current lab outputs give neutral count-505.263158, rounded-505, residual beta0.000625; remaining-carry quotation1356.766903 and six-short gain260302.660320; forward-style carry204.721537 and surplus5.278463. Both outside-bound feasible trade examples yield one currency unit. Complete code and formulas agree.

Selected actual captions inspected: position17 at1450–1800seconds (residual and index replacement), position18 at1640–1900seconds (cash-value normalization and hedge count), position19 at380–930seconds (remaining maturity, count slip, and CAPM approximation) and1390–1740seconds (frictional trade directions). MIT Andrew Lo forward/futures slides25–29 were opened directly. The chapter's adjacent carry/application citation is supported, and additional limitations are its own explicit reconstruction.

Two minor numerical findings were returned to the author and repaired: the printed carry and surplus last decimal now match independently recomputed six-decimal values; the six-contract lab reference constant now equals the true value with absolute tolerance1e-6 and zero relative tolerance. The exact changed lines were re-read, and the full lab rerun before binding these bytes. No substantive algorithm change was needed.

The exposition connects a concrete overlay objective to units, covariance, residuals, and feasible cash-flow accounting. Definitions precede use and the exercises require reconstruction. This full authored-chapter/code review uses selected caption and primary checks; it is not a full independent caption reread, audiovisual audit, human certification, formal proof verification, or replacement for package/browser release validation.


## Bounded LF normalization recheck

Reconstructed the former CRLF bytes from each affected canonical LF file and matched its previously accepted SHA-256 exactly. All unaffected inputs retain their accepted digests. The Python AST is identical and the chapter lab passed a fresh execution. This rebind changes byte-level acceptance only; the full scientific review above remains applicable. Evidence: `validation/line-ending-normalization.json`.
