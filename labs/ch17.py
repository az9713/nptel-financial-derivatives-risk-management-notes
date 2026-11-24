"""Quadratic-variation identities and independently integrated GBM moments."""
from math import exp, isclose, log, pi, sqrt

import numpy as np
from scipy.special import ndtr


def lognormal_parameters(spot, drift, volatility, horizon):
    values = [spot, drift, volatility, horizon]
    if not all(np.isfinite(x) for x in values):
        raise ValueError("parameters must be finite")
    if spot <= 0 or volatility <= 0 or horizon <= 0:
        raise ValueError("spot, volatility, and horizon must be positive")
    return log(spot) + (drift - volatility ** 2 / 2) * horizon, \
        volatility * sqrt(horizon)


def gbm_density(price, spot, drift, volatility, horizon):
    if price <= 0:
        return 0.0
    location, scale = lognormal_parameters(spot, drift, volatility, horizon)
    z = (log(price) - location) / scale
    return exp(-z * z / 2) / (price * scale * sqrt(2 * pi))


def main():
    # Gaussian quadrature checks normal fourth moments independently.
    nodes, weights = np.polynomial.hermite.hermgauss(40)
    z, weights = sqrt(2) * nodes, weights / sqrt(pi)
    assert isclose(float(weights @ (z ** 2)), 1, abs_tol=1e-13)
    assert isclose(float(weights @ (z ** 4)), 3, abs_tol=1e-12)
    assert isclose(2 / (4096 * 0.1 ** 2), 0.048828125, abs_tol=1e-15)
    normalized_exponential = np.exp(0.3 * z - 0.3 ** 2 / 2)
    assert isclose(float(weights @ normalized_exponential), 1,
                   abs_tol=1e-13)
    assert isclose(1.1 * (10 / 11), 1, abs_tol=1e-15)
    # A genuinely random adapted step integrand: two independent increments.
    dw1, dw2 = np.meshgrid(z * sqrt(.5), z * sqrt(.5), indexing='ij')
    joint_weights = weights[:, None] * weights[None, :]
    integral = dw1 + (1 + dw1) * dw2
    variance_by_isometry = .5 + .5 * float(weights @ (1 + z * sqrt(.5))**2)
    assert isclose(float(np.sum(joint_weights * integral)), 0,
                   abs_tol=1e-13)
    assert isclose(float(np.sum(joint_weights * integral**2)), 1.25,
                   abs_tol=1e-12)
    assert isclose(variance_by_isometry, 1.25, abs_tol=1e-13)
    rng = np.random.default_rng(1701)
    steps, horizon = 4096, 1.0
    increments = rng.normal(0, sqrt(horizon / steps), size=steps)
    path = np.r_[0.0, np.cumsum(increments)]
    left_integral = float(path[:-1] @ increments)
    quadratic_sum = float(increments @ increments)
    assert isclose(path[-1] ** 2, 2 * left_integral + quadratic_sum,
                   abs_tol=2e-13)
    print(f"sample quadratic sum={quadratic_sum:.8f}; "
          f"left sum={left_integral:.8f}; endpoint={path[-1]:.8f}")
    for count in [16, 256, 4096]:
        expectation = horizon
        variance = 2 * horizon ** 2 / count
        print(f"n={count}: E[QV]={expectation:.6f}, "
              f"Var[QV]={variance:.8f}")
    spot, drift, volatility, horizon = 100, 0.08, 0.2, 1.0
    location, scale = lognormal_parameters(spot, drift, volatility, horizon)
    prices = np.exp(location + scale * z)
    mean_numeric = float(weights @ prices)
    second_numeric = float(weights @ (prices ** 2))
    mean = spot * exp(drift * horizon)
    variance = spot ** 2 * exp(2 * drift * horizon) * (
        exp(volatility ** 2 * horizon) - 1)
    assert isclose(mean_numeric, mean, rel_tol=1e-12)
    assert isclose(second_numeric - mean_numeric ** 2, variance,
                   rel_tol=1e-11)
    median = exp(location)
    loss_probability = float(ndtr((log(spot) - location) / scale))
    print(f"GBM mean={mean:.8f}, median={median:.8f}, "
          f"variance={variance:.8f}, P[loss]={loss_probability:.8f}")
    # Independent finite-difference test of the forward density PDE.
    for price in [80, 100, 130]:
        dx, dt = price * 1e-4, 1e-4

        def density(s, t):
            return gbm_density(
                s, spot, drift, volatility, t)
        time_derivative = (density(price, 1 + dt)
                           - density(price, 1 - dt)) / (2 * dt)
        flux_plus = drift * (price + dx) * density(price + dx, 1)
        flux_minus = drift * (price - dx) * density(price - dx, 1)

        def diffusion(s):
            return volatility ** 2 * s ** 2 * density(s, 1)
        rhs = -(flux_plus - flux_minus) / (2 * dx) + (
            diffusion(price + dx) - 2 * diffusion(price)
            + diffusion(price - dx)) / (2 * dx ** 2)
        assert isclose(time_derivative, rhs, rel_tol=2e-5, abs_tol=1e-8)
    negative_euler = float(ndtr(-1.0))
    assert isclose(negative_euler, 0.15865525393145707, abs_tol=1e-14)
    from scipy.special import ndtri
    cash_buffer = -2 * float(ndtri(0.05))
    endpoint_risk = float(ndtr(-cash_buffer / 2))
    hitting_risk = 2 * endpoint_risk
    assert isclose(endpoint_risk, 0.05, abs_tol=1e-13)
    assert isclose(hitting_risk, 0.10, abs_tol=1e-13)
    print(f"zero-drift cash buffer={cash_buffer:.8f}: "
          f"endpoint risk={endpoint_risk:.4f}, "
          f"hitting risk={hitting_risk:.4f}")
    print("Ito identity, Gaussian moments, GBM and tail checks passed")


if __name__ == "__main__":
    main()
