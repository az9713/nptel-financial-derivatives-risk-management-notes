"""Synthetic two-asset frontier, tangency, and diversification certificates."""

from math import isclose, isfinite, sqrt


def moments(x):
    return (
        x * 0.08 + (1 - x) * 0.14,
        x * x * 0.01 + (1 - x) ** 2 * 0.04 + 2 * x * (1 - x) * 0.005,
    )


def solve2(a, b, c, rhs):
    determinant = a * c - b * b
    if (
        not all(isfinite(v) for v in (a, b, c, *rhs)) or
        a <= 0 or
        determinant <= 0
    ):
        raise ValueError("Need a positive definite covariance matrix")
    return (
        (c * rhs[0] - b * rhs[1]) / determinant,
        (a * rhs[1] - b * rhs[0]) / determinant,
    )


def main():
    d = 0.01 + 0.04 - 2 * 0.005
    x = (0.04 - 0.005) / d
    mean, variance = moments(x)
    assert isclose(x, 0.875) and isclose(variance, 0.009375)
    for k in range(10001):
        z = -1 + k * 3 / 10000
        assert moments(z)[1] >= variance - 1e-14
        assert isclose(
            moments(z)[1] - variance, d * (z - x) ** 2, abs_tol=1e-14
        )
    try:
        solve2(-1, 0, -1, (1, 1))
    except ValueError:
        pass
    else:
        raise AssertionError("Negative definite matrix accepted")
    q = solve2(0.01, 0.005, 0.04, (0.06, 0.12))
    weights = [v / sum(q) for v in q]
    assert isclose(weights[0], 2 / 3) and isclose(weights[1], 1 / 3)
    tm, tv = moments(weights[0])
    assert isclose(tm, 0.10) and isclose(tv, 1 / 90)
    sharpe = (tm - 0.02) / sqrt(tv)
    # Stationarity links each premium to its covariance with T.
    cov_t = [
        0.01 * weights[0] + 0.005 * weights[1],
        0.005 * weights[0] + 0.04 * weights[1],
    ]
    for premium, covariance in zip((0.06, 0.12), cov_t):
        assert isclose(premium, covariance * (tm - 0.02) / tv)
    assert isclose(0.25 * 0.06**2 * 2 + 0.5 * 0.5 * 0.06**2, 0.0027)
    assert isclose(0.04**2 + 0.002, 0.06**2)
    assert isclose((1.5 * 0.04) ** 2, 0.06**2)
    for count in (1, 10, 100, 1000):
        direct = (count * 0.05 + count * (count - 1) * 0.01) / count**2
        factor = 0.01 + 0.04 / count
        assert isclose(direct, factor)
        assert 0.04 / count < 0.05
    print(
        f"GMV weights=({x:.6f},{1-x:.6f}); mean={mean:.6f}; "
        f"sd={sqrt(variance):.6f}"
    )
    print(
        f"Tangency weights={weights}; mean={tm:.6f}; "
        f"sd={sqrt(tv):.6f}; Sharpe={sharpe:.6f}"
    )
    print(
        "Global quadratic certificate, tangency stationarity, CAPM variance "
        "and diversification checks passed."
    )


if __name__ == "__main__":
    main()
