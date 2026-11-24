"""Seven finite certificates; no network, market data or filesystem effects."""
from fractions import Fraction as F
from math import exp, isclose, isfinite, log, pi, sqrt

import numpy as np
from scipy.integrate import quad
from scipy.optimize import linprog
from scipy.special import ndtr


def tail_es(losses, probabilities, alpha):
    """Average exactly the worst 1-alpha mass of a finite loss law."""
    if not losses or len(losses) != len(probabilities):
        raise ValueError("Need one probability per loss")
    if not all(isfinite(x) for x in [*losses, *probabilities, alpha]):
        raise ValueError("Inputs must be finite")
    if not 0 < alpha < 1 or any(p <= 0 for p in probabilities):
        raise ValueError("Invalid confidence or probability")
    if not isclose(sum(probabilities), 1, abs_tol=1e-12, rel_tol=0):
        raise ValueError("Probabilities must sum to one")
    remaining, total = 1 - alpha, 0.0
    for loss, probability in sorted(zip(losses, probabilities), reverse=True):
        used = min(remaining, probability)
        total += used * loss
        remaining -= used
        if remaining <= 0:
            break
    return total / (1 - alpha)


def affine_kind(a, b, left, right=None):
    """Classify zeros on an exact interval; None is an infinite end."""
    if not all(isinstance(x, F) for x in (a, b, left)):
        raise TypeError("Use exact Fraction coefficients and endpoints")
    if right is not None and not isinstance(right, F):
        raise TypeError("Use a Fraction or None for the right endpoint")
    if left < 0 or (right is not None and right <= left):
        raise ValueError("Invalid nonnegative price interval")
    if a == 0:
        return ('zero_interval', None) if b == 0 else ('no_root', None)
    root = -b / a
    if root >= left and (right is None or root <= right):
        return 'isolated_root', root
    return 'no_root', None


def pricing_check():
    spot, strike, rate, vol, time = 100., 100., .05, .2, 1.
    width = vol * sqrt(time)
    d1 = (log(spot / strike) + (rate + vol**2 / 2) * time) / width
    d2 = d1 - width
    call = spot * ndtr(d1) - strike * exp(-rate * time) * ndtr(d2)

    def discounted_density_payoff(z):
        # Completing the exponent prevents overflow in far-tail quadrature.
        stock_term = spot * exp(-.5 * (z - width)**2)
        strike_term = strike * exp(-rate * time - .5 * z*z)
        return (stock_term - strike_term) / sqrt(2 * pi)

    integral, error = quad(discounted_density_payoff, -d2, np.inf,
                           epsabs=1e-10)
    assert isclose(integral, call, abs_tol=1e-8)
    assert isclose(call, 10.450583572185565, abs_tol=1e-10)
    assert error < 1e-6
    nodes, weights = np.polynomial.hermite.hermgauss(20)
    z = sqrt(2) * nodes
    weights /= sqrt(pi)
    discounted_stock = spot * np.exp(width * z - width**2 / 2)
    assert isclose(float(weights @ discounted_stock), spot, abs_tol=1e-10)
    assert isclose(float(weights @ discounted_stock**2),
                   spot**2 * exp(vol**2 * time), rel_tol=1e-12)
    # Rare-spike sequence: almost-sure convergence does not preserve means.
    for n in (2, 10, 1000):
        assert n * (1 / n) == 1
    print(f"1 pricing: call={call:.8f}; independent integral agrees")


def frontier_check():
    sigma = np.diag([.01, .04, .09])
    mu, target = np.array([.04, .08, .12]), .09
    one = np.ones(3)
    g, j = np.linalg.solve(sigma, one), np.linalg.solve(sigma, mu)
    aa, bb, cc = one @ g, one @ j, mu @ j
    determinant = aa * cc - bb*bb
    assert determinant > 0
    optimal = ((cc - bb*target)*g + (aa*target - bb)*j) / determinant
    constraints = np.vstack([one, mu])
    kkt = np.block([[sigma, -constraints.T],
                    [constraints, np.zeros((2, 2))]])
    solved = np.linalg.solve(kkt, np.array([0, 0, 0, 1, target]))[:3]
    assert np.allclose(optimal, solved)
    assert np.allclose(constraints @ optimal, [1, target])
    h = np.array([.1, -.2, .1])
    assert np.allclose(constraints @ h, 0)
    variance = optimal @ sigma @ optimal
    penalty = (optimal + h) @ sigma @ (optimal + h) - variance
    assert isclose(variance, .022716346153846153, abs_tol=1e-12)
    assert isclose(penalty, h @ sigma @ h, abs_tol=1e-12)
    assert isclose(penalty, .0026, abs_tol=1e-12)
    print(f"2 frontier: variance={variance:.11f}; feasible penalty={penalty}")


def hedge_check():
    factor_cov = np.array([[.04, 0, 0], [0, .01, .006], [0, .006, .01]])
    assert np.linalg.eigvalsh(factor_cov).min() > 0
    loadings = np.array([[1.2, 1, 0], [1, 0, 1]])
    joint = loadings @ factor_cov @ loadings.T
    k_minimum, k_neutral = -joint[0, 1] / joint[1, 1], -1.2
    risks = []
    for k in (k_neutral, k_minimum):
        exposure = np.array([1, k])
        risks.append(float(exposure @ joint @ exposure))
    assert np.allclose(risks, [.01, .00928])
    assert isclose(k_minimum, -1.08)
    assert isclose(1.2 + k_minimum, .12)
    assert isclose(risks[0] - risks[1],
                   joint[1, 1] * (k_neutral - k_minimum)**2)
    print("3 hedge: beta-neutral variance=0.010000; minimum=0.009280")


def mapping_check():
    z, w = np.array([-1, -1, 1, 1]), np.array([-1, 1, -1, 1])
    original, mapped, rest = z, w, -z
    assert np.var(original) == np.var(mapped) == 1
    assert np.var(rest + original) == 0
    assert np.var(rest + mapped) == 2
    covariance_difference = 2 * np.mean(rest * (mapped - original))
    assert covariance_difference == 2
    error, portfolio = mapped - original, rest + original
    assert np.var(portfolio + error) == np.var(error) == 2
    print("4 mapping: equal standalone variance; portfolio variance 0 -> 2")


def es_check():
    losses, probabilities = [0., 10., 100.], [.96, .03, .01]
    for alpha, expected in [(.95, 26), (.96, 32.5), (.975, 46)]:
        actual = tail_es(losses, probabilities, alpha)
        result = linprog(-np.array(losses), A_eq=np.ones((1, 3)),
                         b_eq=[1], bounds=[(0, p / (1-alpha))
                                           for p in probabilities],
                         method='highs')
        assert result.success
        assert isclose(actual, expected, abs_tol=1e-10)
        assert isclose(-result.fun, actual, abs_tol=1e-10)
    for threshold in (0, 2, 7, 10):
        objective = threshold + sum(p * max(loss - threshold, 0)
                                    for p, loss in zip(probabilities, losses)
                                    ) / .04
        assert isclose(objective, 32.5)
    joint_losses, joint_probabilities = [0, 100, 100, 200], [
        .96**2, .96*.04, .04*.96, .04**2]
    combined = tail_es(joint_losses, joint_probabilities, .95)
    individual = tail_es([0, 100], [.96, .04], .95)
    assert isclose(combined, 103.2)
    assert isclose(individual, 80) and combined <= 2 * individual
    for args in [([], [], .95), ([1], [.5], .95),
                 ([1], [1], 1), ([float('nan')], [1], .95)]:
        try:
            tail_es(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid loss law accepted")
    print("5 ES: 95%=26; 96%=32.5; 97.5%=46; aggregated ES=103.2")


def ito_check():
    nodes, weights = np.polynomial.hermite.hermgauss(8)
    weights /= sqrt(pi)
    # For h=1/2, sqrt(2*h) times a Hermite node is the Brownian increment.
    a, b = np.meshgrid(nodes, nodes, indexing='ij')
    joint = weights[:, None] * weights[None, :]
    integral = a + (1 + a) * b
    assert isclose(float(np.sum(joint * integral)), 0, abs_tol=1e-12)
    assert isclose(float(np.sum(joint * integral**2)), 1.25, abs_tol=1e-12)
    assert isclose(.5 + .5 * float(weights @ (1 + nodes)**2), 1.25)
    for n in (4, 16, 64):
        intervals = np.full(n, 1 / n)
        assert isclose(float(intervals.sum()), 1)
        assert isclose(float(2 * intervals @ intervals), 2 / n)
    print("6 Ito: random adapted integral mean=0; second moment=1.25")


def affine_check():
    zero, q = F(0), F(1, 10**14)
    assert affine_kind(q, -100*q, zero) == ('isolated_root', F(100))
    assert affine_kind(zero, -8*q, zero, F(100)) == ('no_root', None)
    assert affine_kind(q, -108*q, F(100)) == ('isolated_root', F(108))
    assert affine_kind(zero, zero, zero) == ('zero_interval', None)
    assert affine_kind(F(1), F(1), zero) == ('no_root', None)
    assert isclose(float(q), 0, abs_tol=1e-12)
    assert isclose(float(-100*q), 0, abs_tol=1e-12)
    assert q*(99-100) < 0 < q*(101-100)

    def call_profit(stock):
        return q * (max(stock - 100, 0) - 8)

    assert call_profit(F(107)) < 0 < call_profit(F(109))
    assert call_profit(F(108)) == 0 and call_profit(F(0)) < 0
    assert F(2, 3) - 1 + F(1, 3) == 0
    assert affine_kind(F(2, 3), F(-62), F(90), F(100))[1] == 93
    assert affine_kind(F(-1, 3), F(38), F(100), F(120))[1] == 114
    assert F(2, 3)*14 - 8 + F(1, 3)*2 == 2
    assert F(20, 3) - 2 == F(14, 3)
    for args in [(1., F(0), F(0)), (F(1), F(0), F(-1)),
                 (F(1), F(0), F(1), F(0))]:
        try:
            affine_kind(*args)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError("Invalid exact interval accepted")
    print("7 affine: isolated roots=100,108; exact butterfly roots=93,114")


if __name__ == '__main__':
    for check in (pricing_check, frontier_check, hedge_check, mapping_check,
                  es_check, ito_check, affine_check):
        check()
    print("All seven finite certificates passed; general proofs remain prose.")
