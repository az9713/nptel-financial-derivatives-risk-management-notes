# References and evidence limits

## The source course

**Prof. J. P. Singh, Financial Derivatives & Risk Management, IIT Roorkee**, NPTEL course 110107128. [Official course page](https://nptel.ac.in/courses/110107128). [Supplied YouTube playlist](https://www.youtube.com/playlist?list=PLLy_2iUCG87CTB2vv9njHaJbmQoa9S5gK).

The [recording map](source-map.html) preserves the supplied upload positions and original titles. Descriptive teaching titles are distinguished from generic upload titles where needed. The introductory recording is retained in the inventory; it is not counted as a missing technical chapter. The put–call-parity upload is linked at its original position and studied with the surrounding option theory.

The course is a source of topic sequence, examples, distinctions, and timestamp locators. This edition independently develops definitions, proofs, numerical constructions, implementations, and solved exercises. When the exposition corrects or narrows a source statement, the source note identifies the distinction. It does not silently attribute the correction to the lecture.

## Supporting primary references

References are integrated beside the claims they support. The following verified introductory sources establish terminology and the boundary between simplified pricing models and market infrastructure:

- **CME Group, Margin: Know What's Needed.** [Official explanation](https://www.cmegroup.com/education/courses/introduction-to-futures/margin-know-what-is-needed). Supports the distinction between futures margin, a purchase down payment, and the funding required after settlement losses.
- **Options Industry Council, Options Basics.** [Official explanation](https://www.optionseducation.org/optionsoverview/options-basics). Supports holder rights, writer obligations, strike, premium, and product-specific exercise/settlement distinctions.
- **CPMI–IOSCO, Principles for Financial Market Infrastructures.** [BIS publication](https://www.bis.org/publications/principles-financial-market-infrastructures). Credit risk, margin, and liquidity risk are treated as management requirements rather than assumed to disappear through clearing.
- **Andrew W. Lo, MIT15.401 Finance Theory I, Forward and Futures Contracts, Fall2008.** [Primary lecture slides](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/a66f697aaeb23b8cfd2bda020172feb5_MIT15_401F08_lec08.pdf). The chapter references identify the relevant contract, financing, and carry passages; historical product examples are not treated as current contract specifications.
- **Leonid Kogan, MIT15.450 Analytics of Finance, Arbitrage-Free Pricing Models, Fall2010.** [Primary lecture notes](https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/219406be97b96bc540e0be6aa778c0b7_MIT15_450F10_lec01.pdf). Supports the distinction between replication, statewise pricing restrictions, and additional factor-model assumptions.
- **NIST/SEMATECH e-Handbook, Linear Least Squares Regression.** [Primary technical reference](https://www.itl.nist.gov/div898/handbook/pmd/section1/pmd141.htm). Supports the least-squares fitting definition and cautions about extrapolation and influential observations.
- **U.S. Treasury, Understanding Pricing and Interest Rates.** [TreasuryDirect](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/). Supports bill-price and rate-convention comparisons. Synthetic calculations retain explicit year fractions and do not infer a current exchange contract from a bill quotation.
- **CME Group, April24,2023 Eurodollar/SOFR conversion announcement.** [Primary announcement](https://www.cmegroup.com/media-room/press-releases/2023/4/24/cme_group_completeskeymilestonesinconversionofeurodollarfutureso.html). Supports the dated transition note separating historical Eurodollar examples from SOFR-based products.

The quantitative development also draws on these primary treatments, with the actual inspected passages stated beside chapter claims and in the reference audit:

- **Andrew W. Lo, Portfolio Theory and The CAPM and APT, MIT15.401.** [Portfolio slides](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/dd628e151309a7f23962b1a31b9356e5_MIT15_401F08_lec13.pdf) and [CAPM slides](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/411d7d9df37d4d0440b18e17e8cea3a9_MIT15_401F08_lec15.pdf). Covariance optimization, diversification, equilibrium assumptions, estimation, and empirical qualifications support the portfolio chapters.
- **Andrew W. Lo, Fixed Income Securities, MIT15.401.** [Primary slides](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/df418b972d36cd53ae5c375b8af61e53_MIT15_401F08_lec04.pdf). Discount factors, forward rates, bond yields, duration, and convexity are compared with independently derived cash-flow models.
- **CME Group, Understanding Treasury Futures.** [Official guide](https://www.cmegroup.com/content/dam/cmegroup/markets/interest-rates/files/understanding-treasury-futures.pdf). Conversion factors, invoices, cheapest-to-deliver selection, and DV01 hedging are used with explicit product and date boundaries.
- **Cox, Ross, and Rubinstein, Option Pricing: A Simplified Approach,1979.** [Author manuscript](https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/7/36891/files/2017/07/CRR79-1yy8av8.pdf). The inspected replication and limiting-distribution passages support the discrete-market argument; complete-paper review is not claimed.
- **Leonid Kogan, Stochastic Calculus and Option Pricing, MIT15.450.** [Primary lecture notes](https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/0d1260b891a96241316d883d4f5bfaec_MIT15_450F10_lec02.pdf). Brownian increments, quadratic variation, Itô calculus, self-financing, and the diffusion-pricing PDE supply an integrated mathematical comparison.
- **MIT18.S096, Lecture18: Itô Calculus.** [Primary lecture notes](https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/ef2c66c8079ba656210ad1fd4a5e2fa8_MIT18_S096F13_lecnote18.pdf). Theorem1.1 and Example1.3 support the general transformation and stochastic square example. The edition states the sampled-integrand approximation conditions separately.
- **Steven Lalley, Brownian Motion and Change of Measure.** [Reflection principle](https://www.stat.uchicago.edu/~lalley/Courses/312/BrownianMotion312.pdf) and [Novikov/Girsanov notes](https://galton.uchicago.edu/~lalley/Courses/390/Lecture10.pdf). These identify the stopping-time and true-martingale requirements behind the path-event and measure-change arguments.

- **Marco Bianchetti, Two Curves, One Price; Federal Reserve Bank of New York, SOFR methodology.** [Primary pricing slides](https://www.bianchetti.org/Finance/2009-11-QCE-DoubleCurvePricingSlides-v1.1.pdf) and [administrator methodology](https://www.newyorkfed.org/markets/reference-rates/additional-information-about-reference-rates). The swap chapter identifies the inspected passages and distinguishes a one-curve replication model, separate projection/discount curves, and overnight compounding conventions.
- **Rockafellar and Uryasev, Conditional Value-at-Risk for General Loss Distributions.** [Primary manuscript](https://sites.math.washington.edu/~rtr/papers/rtr187-CVaR2.pdf), especially Definition3, Proposition8, and Theorem10. Probability atoms require a precisely defined tail average; the risk chapter distinguishes this general result from the continuous-distribution setting of their [earlier CVaR paper](https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf).

Further primary references and exact supporting locators appear in the relevant chapters. External research findings remain attributed to their authors. Technical access to a document does not imply a right to redistribute its full text; downloaded research copies remain local.

## Source coverage is not a single completeness flag

The source manifest records the acquired caption representation, language/provenance, durations, and content digests. A complete textual reading can establish topic coverage without establishing that every equation visible on a board was transcribed correctly. The source-reading ledgers report the actual acquisition and reading scope. Comprehensive real-time viewing, listening, or experimental reproduction is not claimed unless separately recorded.

The notes reconstruct equations and test examples rather than claiming a verbatim transcript. Where a result requires a theorem beyond the developed setting, its supporting source and assumptions are identified. New synthetic examples are marked as teaching constructions. No timestamp is used as a percentage-of-reuse estimate.

## What the validation evidence means

Scientific/editorial receipts record independent AI review of the specified manuscripts, metadata, and labs at exact content digests. Runtime evidence records actual completion of the specified programs. Browser checks record mathematical rendering, layout, and controls at the listed viewports. A reproducibility check records whether public authored inputs regenerate the committed edition without private acquisition files.

These are different tests. An accepted manuscript does not prove that a still-running lab finished. A green browser check does not prove a financial theorem. A matching live-file digest establishes publication integrity, not scientific truth. Two independent AI reviews are stronger evidence than a single unchecked draft, but are not human expert certification or formal verification.

## Historical contracts and current practice

The source course includes historical interest-rate instruments and conventions. Those examples remain useful for understanding quotation, accrual, basis, and hedge units. A historical Eurodollar example must not be read as a current listing or settlement specification. Current comparisons use dated primary exchange sources and identify where SOFR products differ.

All worked market numbers are synthetic unless explicitly attributed and dated. Contract multipliers, legal terms, margin rules, and rate benchmarks must be checked in current official documentation before any real application. The teaching code neither accesses an account nor places orders.
