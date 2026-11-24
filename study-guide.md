# Study guide

The book can be read in source-topic order or along a focused route. The dependencies matter: a hedge is easier to assess after its cash flows and units are explicit, and a pricing measure is easier to understand after one-step replication.

## The cash-flow and hedging route

Read Chapters [1](ch01.html)–[5](ch05.html) for forwards, futures, clearing, basis, and minimum-variance hedging. Read [6](ch06.html) for the portfolio beta used in index hedging, then [7](ch07.html) for index exposure, [8](ch08.html)–[12](ch12.html) for rate and bond contracts, and [22](ch22.html) for swap payments and valuation.

Keep a ledger with five columns: date, currency, reference quantity, cash-flow rule, and responsible party. Many errors become visible before any calculus: a hedge uses the wrong sign, a rate quote is applied with the wrong day count, or an interim margin payment is omitted from the funding analysis.

## The mathematical pricing route

Start with [1](ch01.html) and [2](ch02.html) for statewise cancellation and replication. Chapters [13](ch13.html)–[15](ch15.html) develop option identities, inequalities, early exercise, and static strategies. Chapters [16](ch16.html)–[19](ch19.html) build stochastic processes, discrete replication, measure change, and the Black–Scholes framework. Chapters [20](ch20.html) and [21](ch21.html) translate the model into sensitivities and finite hedges.

For each theorem, write its assumptions beside the conclusion. For each pricing calculation, identify the numeraire or discount convention, the probability measure if one is used, and which claims the available securities can replicate. A probability appearing in a valuation formula is not automatically a prediction of how often the corresponding state will occur.

## The portfolio-risk route

Read [5](ch05.html) and [6](ch06.html) for covariance, projection, diversification, and the assumptions behind CAPM. Read [9](ch09.html) for duration-based approximations, [20](ch20.html)–[21](ch21.html) for nonlinear sensitivities, and [23](ch23.html)–[24](ch24.html) for quantiles, expected shortfall, nonlinear revaluation, and risk diagnostics.

Specify the sign of loss before calculating a quantile. Specify the holding period and whether positions are fixed or rebalanced. Compare a linear approximation with direct revaluation on at least one adverse scenario. A small estimated variance or a reported VaR does not establish a maximum possible loss.

## A repeatable study session

1. Read the opening problem and predict which quantities should cancel or remain uncertain.
2. Reconstruct the central derivation without consulting the next line. Name the assumption used at the consequential step.
3. Check the worked numerical example, including currency, accrual fraction, rate units, and position sign.
4. Run the lab in a fresh interpreter. Change one input within its domain, then deliberately test a violated assumption and inspect the failure behavior.
5. Solve the exercises before opening their solutions. Compare the reasoning, not only the numerical answer.
6. Return to the opening problem. State which decision the result supports and which omitted risk would require a richer model.

## Reading mathematical results correctly

For seven complete examples of this discipline, read [Seven mathematical repairs](mathematical-repairs.html). Each begins with the earlier gap and completes the missing argument. Its [laboratory](labs/mathematical-repairs.py) checks the constructions independently of the prose. The first and sixth issues share the stochastic-integral foundation from Chapter 17; the remaining issues can be read independently with elementary probability and linear algebra.

A **definition** fixes a convention. A **derived identity** follows algebraically under its stated model. A **theorem** has hypotheses and a proof or an explicitly cited supporting result. A **numerical check** examines particular finite calculations. An **empirical finding** needs data and a measurement procedure. Their roles are complementary, but success in one category does not promote a claim to another.

The chapter solutions expose intermediate steps rather than functioning as an answer key. The labs use assertions and independent checks when practical. Use the references beside the relevant claim to inspect an external result; a long bibliography is not a substitute for understanding the argument.

## Three capstone investigations

**Separate replication from forecasting.** Start with the one-step market in [Chapter18](ch18.html). Keep stock outcomes, bank growth, and the call payoff fixed while changing the physical up probability. Record the physical expected payoff, the replicating cost, and the pricing weight separately. Then add a third state and find a payoff outside the span of stock and cash. The deliverable is a cash-flow certificate showing which prices are forced and which form an interval. A predictive model of returns answers a different question from a no-arbitrage price restriction.

**Break an apparently perfect hedge.** Combine [Chapter9](ch09.html)'s curve exposures with [Chapter12](ch12.html)'s bond-futures hedge. First match value sensitivity to a parallel rate shift; then apply a curve twist and recompute every cash flow. Change the cheapest-to-deliver bond in a separate scenario. Report residual value risk, contract rounding, basis, and interim funding as separate quantities. This makes model failure informative: matching one derivative of value does not cancel every direction in the yield curve.

**Audit a risk engine before adding machine learning.** Use [Chapter23](ch23.html) and [Chapter24](ch24.html) to build a loss table with a point mass at the chosen quantile, a rare severe loss, and an option portfolio requiring nonlinear repricing. Compare quantile VaR, atom-aware expected shortfall, delta-normal loss, delta–gamma loss, and exact scenario revaluation. If fitting a neural pricing or risk surrogate, test the payoff-appropriate monotonicity, convexity, parity, approximation error, and tail behavior against these known constructions before optimizing predictive accuracy. A surrogate can reproduce an invalid target very accurately; the mathematical certificates determine what the target should satisfy.

Each project should include a model statement, units and signs, a reproducible numerical result, a deliberately broken assumption, and a precise boundary on the conclusion. Synthetic experiments test an implementation and its logic. An empirical market claim additionally needs dated data, a sampling protocol, and an out-of-sample evaluation.
