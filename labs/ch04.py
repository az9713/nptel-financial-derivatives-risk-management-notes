"""Exposure projections and hedge accounting on finite synthetic scenarios."""

from math import isclose, isfinite


def mean(values):
    return sum(values) / len(values)


def covariance(x, y):
    return mean([(a - mean(x)) * (b - mean(y)) for a, b in zip(x, y)])


def exposure(x, y):
    x, y = list(x), list(y)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Need equal arrays with at least two observations")
    if not all(isfinite(v) for v in x + y):
        raise ValueError("Observations must be finite")
    var_x = covariance(x, x)
    if var_x <= 0:
        raise ValueError("Regressor needs positive variance")
    beta = covariance(x, y) / var_x
    alpha = mean(y) - beta * mean(x)
    residual = [b - alpha - beta * a for a, b in zip(x, y)]
    return alpha, beta, residual


def main():
    x = [-2, -1, 0, 1, 2]
    y = [5, 5, 10, 11, 19]
    alpha, beta, residual = exposure(x, y)
    var_y = covariance(y, y)
    var_e = covariance(residual, residual)
    assert isclose(mean(residual), 0, abs_tol=1e-12)
    assert isclose(covariance(x, residual), 0, abs_tol=1e-12)
    assert isclose(var_y, beta**2 * covariance(x, x) + var_e)
    spot, future, opening = 65, 66, 72
    short_revenue = spot + (opening - future)
    long_cost = spot - (future - opening)
    assert short_revenue == long_cost == opening + (spot - future) == 71
    near = [98 + 101 - 99, 105 + 101 - 106]
    distant = [98 + 104 - 100, 105 + 104 - 110]
    assert near == [100, 100] and distant == [102, 99]
    # Zero linear exposure leaves nonlinear variation.
    nonlinear_x = [-1, 0, 1]
    nonlinear_y = [v**2 for v in nonlinear_x]
    _, zero_beta, nonlinear_e = exposure(nonlinear_x, nonlinear_y)
    assert zero_beta == 0
    assert isclose(covariance(nonlinear_e, nonlinear_e), 2 / 9)
    print(
        f"alpha={alpha:.6f}; beta={beta:.6f}; "
        f"total_variance={var_y:.6f}; residual_variance={var_e:.6f}"
    )
    print(
        f"matched_short_revenue={short_revenue}; matched_long_cost={long_cost}"
    )
    print(
        f"near_contract_effective_prices={near}; "
        f"distant_contract_effective_prices={distant}"
    )
    print(
        "Projection orthogonality, variance decomposition, basis signs "
        "and zero-beta nonlinear-risk checks passed."
    )


if __name__ == "__main__":
    main()
