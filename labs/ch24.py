"""Portfolio covariance, nonlinear losses, finite-tail and backtest checks."""

from math import comb, exp, fsum, isclose, log, pi, sqrt
from statistics import NormalDist

import numpy as np
from scipy.special import ndtr


def covariance_risk(exposure, covariance):
    exposure = np.asarray(exposure, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    if covariance.shape != (exposure.size, exposure.size):
        raise ValueError("Covariance shape must match exposure")
    if not np.isfinite(exposure).all() or not np.isfinite(covariance).all():
        raise ValueError("Finite exposures and covariance required")
    if not np.allclose(covariance, covariance.T, atol=1e-15, rtol=0):
        raise ValueError("Covariance must be symmetric")
    eigenvalues = np.linalg.eigvalsh(covariance)
    scale = max(float(np.max(np.abs(covariance))), 1e-300)
    if eigenvalues.min() < -1e-12 * scale:
        raise ValueError("Covariance must be positive semidefinite")
    return sqrt(max(float(exposure @ covariance @ exposure), 0))


def finite_tail(losses, probabilities, alpha):
    """Left quantile and worst (1-alpha) probability mass, with split atoms."""
    pairs = sorted(zip(losses, probabilities))
    if not 0 < alpha < 1 or not pairs:
        raise ValueError("Need nonempty distribution and 0 < alpha < 1")
    if len(losses) != len(probabilities):
        raise ValueError("Need one probability per loss")
    if not all(np.isfinite(x) and np.isfinite(p) and p >= 0 for x, p in pairs):
        raise ValueError("Finite losses and nonnegative masses required")
    total = fsum(p for _, p in pairs)
    if not isclose(total, 1, rel_tol=0, abs_tol=1e-12):
        raise ValueError("Probability mass must sum to one")
    pairs = [(loss, probability / total) for loss, probability in pairs]
    cumulative, quantile = [], None
    for loss, probability in pairs:
        cumulative.append(probability)
        if fsum(cumulative) >= alpha:
            quantile = loss
            break
    remaining, tail_total = 1 - alpha, 0.0
    for loss, probability in reversed(pairs):
        used = min(probability, remaining)
        tail_total += used * loss
        remaining -= used
        if remaining <= 1e-15:
            break
    return quantile, tail_total / (1 - alpha)


def call_and_greeks(spot, strike=100, rate=0.02, sigma=0.2, tau=0.25):
    width = sigma * sqrt(tau)
    d1 = (log(spot / strike) + (rate + sigma * sigma / 2) * tau) / width
    call = spot * ndtr(d1) - strike * exp(-rate * tau) * ndtr(d1 - width)
    delta = ndtr(d1)
    gamma = exp(-d1 * d1 / 2) / (sqrt(2 * pi) * spot * width)
    return call, delta, gamma


def main():
    z90 = NormalDist().inv_cdf(0.9)
    bond_sigma = 6e6 * 5.2 * 0.0009
    rounded_var = 1.28 * sqrt(20) * bond_sigma
    precise_var = z90 * sqrt(20) * bond_sigma
    assert bond_sigma == 28080
    print(
        f"Source bond daily sd={bond_sigma:.6f}; "
        f"20d VaR with1.28={rounded_var:.6f}, precise={precise_var:.6f}"
    )
    derivative_cov = [
        [0.02**2, 0.3 * 0.02 * 0.01],
        [0.3 * 0.02 * 0.01, 0.01**2],
    ]
    derivative_sigma = covariance_risk(
        [1000 * 120, 20000 * 30], derivative_cov
    )
    assert isclose(derivative_sigma, sqrt(50_400_000))
    assert covariance_risk([1, -1], [[1, 1], [1, 1]]) == 0
    try:
        covariance_risk([1, 1], [[1, 2], [2, 1]])
    except ValueError:
        pass
    else:
        raise AssertionError("Indefinite covariance accepted")

    sa, sb, rho, target = 0.0006, 0.001, 0.9, 0.00068
    polynomial = [
        sa * sa + sb * sb - 2 * rho * sa * sb,
        -2 * sb * sb + 2 * rho * sa * sb,
        sb * sb - target * target,
    ]
    roots = np.roots(polynomial)
    weights = [
        float(w.real)
        for w in roots
        if abs(w.imag) < 1e-12 and 0 <= w.real <= 1
    ]
    assert len(weights) == 1
    w = weights[0]
    mapped_variance = (
        w * w * sa * sa
        + (1 - w) ** 2 * sb * sb
        + 2 * w * (1 - w) * rho * sa * sb
    )
    assert isclose(mapped_variance, target**2, rel_tol=1e-12)
    pv = 50000 / (1.056**0.3)
    assert not isclose(0.25 * w + 0.5 * (1 - w), 0.3)
    print(
        f"Source mapping PV={pv:.6f}; short bucket weight={w:.9f}; "
        f"allocations={pv*w:.6f}/{pv*(1-w):.6f}"
    )
    pca_sigma = sqrt(6**2 * 20**2 + (-4) ** 2 * 8**2)
    print(
        f"Source option sd={derivative_sigma:.6f}; "
        f"PCA sd={pca_sigma:.6f},5d90VaR={z90*sqrt(5)*pca_sigma:.6f}"
    )
    foreign_leg, domestic_leg = 1e6 * 1.53 * 0.975, 1.5e6 * 0.97
    fx_sigma = covariance_risk(
        [foreign_leg, -domestic_leg],
        [
            [0.0006**2, 0.8 * 0.0006 * 0.0005],
            [0.8 * 0.0006 * 0.0005, 0.0005**2],
        ],
    )
    wrong_sign = covariance_risk(
        [foreign_leg, domestic_leg],
        [
            [0.0006**2, 0.8 * 0.0006 * 0.0005],
            [0.8 * 0.0006 * 0.0005, 0.0005**2],
        ],
    )
    assert fx_sigma < wrong_sign
    print(
        f"Synthetic FX-forward value={foreign_leg-domestic_leg:.6f}; "
        f"sd={fx_sigma:.6f}; wrong-sign sd={wrong_sign:.6f}"
    )
    covariance = np.array([[0.0001, 0.000099], [0.000099, 0.0001]])
    values, vectors = np.linalg.eigh(covariance)
    exposure = np.array([1e6, -1e6])
    loadings = vectors.T @ exposure
    contribution = loadings**2 * values
    assert isclose(values[-1] / sum(values), 0.995)
    assert isclose(sum(contribution), 2e6)
    assert contribution[-1] < 1e-20

    c0, delta, gamma = call_and_greeks(100)
    shocks = [-20, -10, 0, 10, 20]
    probabilities = [0.01, 0.09, 0.8, 0.09, 0.01]
    exact = [
        100 * (call_and_greeks(100 + x)[0] - c0 - delta * x) for x in shocks
    ]
    quadratic = [100 * gamma * x * x / 2 for x in shocks]
    assert min(exact) >= -1e-10
    assert max(exact) > 0
    exact_tail = finite_tail(exact, probabilities, 0.95)
    quadratic_tail = finite_tail(quadratic, probabilities, 0.95)
    print("Short-call delta-hedged exact losses", [round(x, 6) for x in exact])
    print(
        f"Linear VaR=0; gamma VaR/ES={quadratic_tail}; "
        f"exact VaR/ES={exact_tail}"
    )
    atom_tail = finite_tail([0, 10, 100], [0.90, 0.08, 0.02], 0.95)
    assert isclose(atom_tail[0], 10) and isclose(atom_tail[1], 46)
    assert finite_tail([0, 1000], [0.99, 0.01], 0.95)[0] == 0
    assert isclose(finite_tail([0, 1000], [0.99, 0.01], 0.95)[1], 200)

    # Exact normal moments of a symmetric quadratic: finite Rademacher grid
    # is inappropriate for fourth moments, so verify using normal quadrature.
    from numpy.polynomial.hermite import hermgauss

    nodes, masses = hermgauss(12)
    normal_nodes, masses = sqrt(2) * nodes, masses / sqrt(pi)
    loss = 2 + 3 * normal_nodes + 0.5 * 4 * normal_nodes**2
    mu = sum(masses * loss)
    variance = sum(masses * (loss - mu) ** 2)
    assert isclose(mu, 2 + 0.5 * 4)
    assert isclose(variance, 3**2 + 0.5 * 4**2)

    value = 1e6 * exp(-0.04 * 5)
    exact_bond_loss = value * (1 - exp(-0.01 * 5))
    linear_bond_loss = value * 5 * 0.01
    gamma_bond_loss = value * (5 * 0.01 - 0.5 * 25 * 0.01**2)
    assert gamma_bond_loss < exact_bond_loss < linear_bond_loss
    print(
        f"5y zero100bp loss exact={exact_bond_loss:.6f}; "
        f"linear={linear_bond_loss:.6f}; quadratic={gamma_bond_loss:.6f}"
    )
    n, p = 250, 0.01
    tail10 = fsum(
        comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(10, n + 1)
    )
    assert isclose((1 - p) ** n, 0.08105851616218128)
    clustered = [1] * 10 + [0] * 240
    spread = [int(i % 25 == 0) for i in range(250)]
    assert sum(clustered) == sum(spread) == 10
    assert sum(a * b for a, b in zip(clustered, clustered[1:])) == 9
    assert sum(a * b for a, b in zip(spread, spread[1:])) == 0
    print(
        f"IID 250day99% expected exceptions={n*p}; "
        f"P(no exceptions)={(1-p)**n:.8f}; P(K>=10)={tail10:.8f}"
    )
    print(
        "Covariance, mapping, PCA, nonlinear-tail and backtest checks passed."
    )


if __name__ == "__main__":
    main()
