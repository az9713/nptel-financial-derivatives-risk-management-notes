"""Currency and finite-tail checks; no filesystem or network effects."""

from fractions import Fraction
from math import ceil, exp, isclose, isfinite, sqrt

import numpy as np
from scipy.special import ndtri
from scipy.optimize import linprog


def close(actual, expected, tolerance=1e-8):
    assert isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (
        actual, expected
    )


def law(losses, probabilities):
    if len(losses) != len(probabilities) or not losses:
        raise ValueError(
            "Require matching nonempty loss and probability lists")
    if not all(isfinite(x) for x in (*losses, *probabilities)):
        raise ValueError("Losses and probabilities must be finite")
    weights = [Fraction(str(p)) for p in probabilities]
    if min(weights) < 0 or sum(weights) != 1:
        raise ValueError("Probabilities must be nonnegative and sum to one")
    return sorted(zip(losses, weights))


def risk(losses, probabilities, alpha):
    """Lower quantile and exact-probability tail filling, including atoms."""
    alpha = Fraction(str(alpha))
    if not 0 < alpha < 1:
        raise ValueError("Confidence must lie strictly between zero and one")
    distribution = law(losses, probabilities)
    cumulative = Fraction(0)
    for loss, weight in distribution:
        cumulative += weight
        if cumulative >= alpha:
            var = loss
            break
    remaining = 1 - alpha
    tail_value = 0
    for loss, weight in reversed(distribution):
        included = min(weight, remaining)
        tail_value += loss * float(included)
        remaining -= included
        if remaining == 0:
            break
    es = tail_value / float(1 - alpha)
    return var, es


def es_objective(losses, probabilities, alpha):
    """Independent convex-breakpoint minimization for a finite distribution."""
    law(losses, probabilities)
    return min(a + sum(p * max(loss - a, 0)
                       for loss, p in zip(losses, probabilities)) / (1 - alpha)
               for a in losses)


def empirical_var(losses, alpha):
    if not losses or not 0 < alpha < 1:
        raise ValueError("Require losses and an interior confidence")
    rank = ceil(len(losses) * Fraction(str(alpha)))
    return sorted(losses)[rank - 1]


def main():
    times = (1, 2, 3)
    yen_cash, dollar_cash = (60, 60, 1260), (.8, .8, 10.8)
    yen_bond = sum(c * exp(-.04 * t) for c, t in zip(yen_cash, times))
    dollar_bond = sum(c * exp(-.09 * t) for c, t in zip(dollar_cash, times))
    spot = 1 / 110
    leg_value = spot * yen_bond - dollar_bond
    converted = sum(exp(-.09 * t) * (spot * exp(.05 * t) * y - d)
                    for t, y, d in zip(times, yen_cash, dollar_cash))
    close(leg_value, converted)
    close(leg_value, 1.542995774688313)
    h = .01
    inverse_derivative = ((yen_bond / (110 + h) - dollar_bond)
                          - (yen_bond / (110 - h) - dollar_bond)) / (2 * h)
    close(inverse_derivative, -yen_bond / 110**2, tolerance=2e-8)
    print(f"Source swap {leg_value:.8f} million dollars; "
          f"value at 100 yen/dollar {yen_bond / 100 - dollar_bond:.8f}")
    for fx, expected in ((.45, 31000), (.65, -13000)):
        close(130000 - 220000 * fx, expected)
    close(130000 - 220000 * .55, 9000)
    # Repaired matched notionals and complete intermediary flow amounts.
    close(20e6 * .5, 10e6)
    close(10e6 * .063 - 10e6 * .05, 130000)
    close(20e6 * .069 - 20e6 * .08, -220000)

    losses, probabilities = [0, 10, 100], [.96, .03, .01]
    for alpha, expected in ((.95, (0, 26)), (.975, (10, 46))):
        var, es = risk(losses, probabilities, alpha)
        close(var, expected[0])
        close(es, expected[1])
        close(es, es_objective(losses, probabilities, alpha))
        print(f"Finite law alpha={alpha}: VaR={var}, ES={es:.8f}")
    # Independent LP solves the bounded probability-reweighting formulation.
    for alpha in (.95, .96, .975):
        bounds = [(0, p / (1 - alpha)) for p in probabilities]
        result = linprog(-np.asarray(losses, float), A_eq=[[1, 1, 1]],
                         b_eq=[1], bounds=bounds,
                         method='highs')
        assert result.success
        close(-result.fun, risk(losses, probabilities, alpha)[1])
        close(sum(result.x), 1)
        assert min(result.x) >= 0
    for threshold in (0, 2, 7, 10):
        objective = threshold + sum(p * max(loss - threshold, 0)
                                    for p, loss in zip(probabilities, losses)
                                    ) / .04
        close(objective, 32.5)
    close(risk([0, 10, 1000], probabilities, .95)[1], 206)
    close(sum(x * p for x, p in zip(losses, probabilities)), 1.3)
    close((.03 * 10 + .01 * 100) / .04, 32.5)
    close(risk([-5], [1], .95)[0], -5)
    close(empirical_var(list(range(1, 501)), .99), 495)
    close(empirical_var(list(range(1, 21)), .9), 18)
    close(empirical_var(list(range(1, 21)), .95), 19)
    joint = ((1.1, .9), (.9, 1.1))
    scrambled = ((1.1, 1.1), (.9, .9))
    joint_losses = [12000 * (1 - stock * fx) for stock, fx in joint]
    scrambled_losses = [12000 * (1 - stock * fx) for stock, fx in scrambled]
    close(empirical_var(joint_losses, .95), 120)
    close(empirical_var(scrambled_losses, .95), 2280)
    single = risk([0, 100], [.96, .04], .95)
    combined = risk([0, 100, 200], [.9216, .0768, .0016], .95)
    close(single[0], 0)
    close(single[1], 80)
    close(combined[0], 100)
    close(combined[1], 103.2)
    assert combined[0] > 2 * single[0]
    assert combined[1] <= 2 * single[1]

    z = ndtri(.99)
    one_asset = 100000 * .3 * sqrt(5 / 252) * z
    rounded = 100000 * .3 * sqrt(5 / 252) * 2.33
    two_assets = sqrt(2.6e6 * 5) * z
    print(f"Source five-day VaR exact {one_asset:.8f}; z = 2.33 {rounded:.8f}")
    print(f"Source two-asset five-day VaR {two_assets:.8f}")
    variance_factor = 5 + 2 * sum((5 - k) * .4**k for k in range(1, 5))
    covariance = np.array([[.4**abs(i - j) for j in range(5)]
                          for i in range(5)])
    close(variance_factor, float(np.ones(5) @ covariance @ np.ones(5)))
    close(variance_factor, 9.4672)
    assert np.linalg.eigvalsh(covariance).min() > 0
    print(f"Autocorrelation variance multiplier {variance_factor}; "
          f"SD ratio {sqrt(variance_factor / 5):.8f}")
    normal_var = 100000 * .3 * sqrt(5 / 252) * z
    exact_gbm_var = 100000 * (1 - exp(-.3**2 / 2 * 5 / 252
                                      - .3 * sqrt(5 / 252) * z))
    assert 0 < exact_gbm_var < 100000
    assert exact_gbm_var != normal_var
    try:
        risk([0, 1], [.9, .2], .95)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid probability law accepted")
    print("All currency, quantile, atom-safe ES, and horizon checks passed.")


if __name__ == '__main__':
    main()
