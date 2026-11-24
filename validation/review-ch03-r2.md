# Independent scientific and editorial review: Chapter 03

## Verdict

Accepted at the current manuscript, metadata, and laboratory hashes in the companion receipt. The reviewer did not author this chapter. All six exercise solutions and the complete code were checked. No unresolved finding remains.

## Mathematical and accounting checks

The signed settlement rule and telescoping sum are correct. The synthetic margin table respects its strict maintenance threshold: the balance of400 causes no top-up, while the later300 balance requires300 to restore600. The closing1100 balance less total external deposits900 gives profit200. The early-close example correctly separates a released collateral balance from a realized trading loss.

The deterministic-rate scaling is predictable and produces the one-unit terminal forward payoff after financing each settlement. The fixed-position accumulated example is5.051, while the scaled construction gives5. The random-discount covariance identity is correct under the explicitly stated pricing/continuous-settlement framework; it is marked as a preview rather than claimed to follow from the elementary margin ledger. Its two-state benchmark calculation and interpretation of dependence are consistent.

All six solutions reconstruct the mechanisms. The distinction among notional, collateral, trading profit, liquidity need, and credit exposure is maintained. Fractional scalability, symmetric funding, default-free model performance, and the historical/current product boundary are stated where they matter. The lab completed in a fresh process and its actual outputs agree with the prose and independently checked arithmetic.

## Sources and teaching

Selected source cues from position7 around294–488seconds and position8 around462–618seconds were checked for margin layers, the modeled percentile, and the deterministic financing/scaling setup. The author's complete sequential reading ledger is separate evidence. MIT Lo slides12–16 support the settlement/margin description. The downloaded primary BIS PFMI text at PDFpage57 was inspected directly; paragraphs3.6.1–4 distinguish close-out initial margin, current variation margin, modeled confidence, and the need for reliable prices. The chapter correctly rejects literal risk elimination.

The purchasing-manager case and dated ledger give the abstraction an operational meaning. Definitions precede their use, the code implements the already explained model, and prose develops the comparison instead of substituting a formula list. No unsupported current contract specification is introduced.

## Scope limits

Full scientific/editorial manuscript, metadata, solution, and code review; fresh lab execution; selected source and primary-reference verification. This reviewer did not reread every caption in the three recordings or inspect the full audiovisual material. Browser behavior and the other independent review remain separate gates. AI review is not human expert certification or formal proof verification.

## Listing-format recheck

The final PEP8/79-column laboratory was read in full after formatting and executed again. The reviewed mathematical expressions and certificate outputs remain consistent. The current lab digest is rebound in the receipt; manuscript and metadata bindings are unchanged. This bounded code recheck does not imply another full source audit.

Final canonical-line-ending recheck: the lead reviewer independently reconstructed the prior CRLF bytes from the LF version and matched the previous accepted SHA-256 for every changed bound file. Laboratory ASTs also match. This newline-only operation changes no scientific text or code behavior; the receipt now binds the canonical LF bytes. Evidence: `validation/line-ending-normalization.json`.
