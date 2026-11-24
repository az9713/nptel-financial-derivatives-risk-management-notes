# Independent scientific and editorial review: Chapter 06

## Verdict

Accepted after the repairs below, at the current manuscript, metadata, and laboratory digests in the companion receipt. This reviewer did not author the chapter. The entire text, all six solutions, and complete code were checked. The lab ran in a fresh process before and after the repairs.

## Repaired findings

The opening phrase about securities promising an expected return was replaced by a modeled expectation, preserving the distinction between a moment input and a contractual promise. The two-by-two covariance solver initially checked only a positive determinant, which also admits negative-definite matrices. The author added finite-input validation and a positive leading diagonal condition, together with a negative-definite rejection check. The final listing meets the stated PEP8/79-column standard. No finding remains.

## Mathematical and numerical review

The covariance expansion, positive-semidefinite covariance argument, two-asset GMV derivative, and completed-square global certificate are correct. Long-only projection and degenerate/perfect-correlation geometric qualifications are explicit. The synthetic GMV allocation is0.875/0.125 with mean0.0875 and variance0.009375.

The covariance-metric Cauchy–Schwarz bound gives the tangency direction under positive definiteness. The positive-normalization and positive-premium conditions prevent the squared-ratio argument from being mistaken for an unconditional long-only solution. The independently checked inverse-covariance direction is4.8/2.4, normalized to2/3 and1/3, with mean0.10, variance1/90, and Sharpe ratio0.758947.

The CAPM perturbation derivative is correct for interior feasible trades. The chapter states the additional common-opportunity, mean–variance, expectations, financing, and market-clearing assumptions needed to identify the maximizing portfolio with the market. Regression orthogonality is distinguished from that equilibrium restriction and from independence. The three beta/residual examples correctly separate total volatility from expected premium and from leverage.

The average-covariance counting formula and limiting conditions are correct. Its independent-return and common-factor examples identify why a diversification floor may or may not remain. All six worked solutions reconstruct their claims. Fresh lab outputs and the explicit invalid-covariance rejection agree with the text.

## Sources and editorial scope

The independently retrieved MIT Lo portfolio and CAPM primary notes support the cited subject structure; selected covariance, tangency, market-portfolio, and beta material was checked. The author's full source-reading ledger is separate evidence. This reviewer did not reread all three complete caption sources or perform an audiovisual audit.

The chapter develops a persistent synthetic portfolio through covariance, optimization, and equilibrium while keeping the logical status of those steps separate. Definitions and horizon/rate conventions precede substantive use. Its mathematics is not replaced by market claims or historical examples treated as current data. This full scientific/editorial code-and-solution review remains separate from the first independent review and package/browser/release checks. No human expert certification or formal proof verification is claimed.

Final canonical-line-ending recheck: the lead reviewer independently reconstructed the prior CRLF bytes from the LF version and matched the previous accepted SHA-256 for every changed bound file. Laboratory ASTs also match. This newline-only operation changes no scientific text or code behavior; the receipt now binds the canonical LF bytes. Evidence: `validation/line-ending-normalization.json`.


## Critical parity revision, 24 November 2026

Read the complete new many-asset frontier subsection and adjacent two-asset/frontier material, the added lab certificate, and objective metadata. Verified the Gram determinant condition, both equality constraints, vanishing cross term, strict global variance gap, GMV completion, and singular/equal-mean/long-only boundaries. An independent full KKT solve matched the claimed constrained solution in 25 seeded positive-definite four-asset cases; random feasible perturbations matched the exact variance gaps. Fresh chapter lab passed. Requested and verified the clarification unrestricted-weight model.

Accepted after the described incremental review. The earlier full-review scope remains historical; no repeated source or audiovisual audit is claimed. Current exact file bindings and prior bindings appear in the JSON receipt. Reviewer remains independent of the chapter author.
