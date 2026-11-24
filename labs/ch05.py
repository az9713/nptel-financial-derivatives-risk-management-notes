"""Minimum-variance sizing, integer rounding, and regime-change checks."""

from math import floor, isclose, isfinite, sqrt


def sizing(quantity, multiplier, sigma_s, sigma_f, rho):
    """Return h, signed short count n_s, integer short count, and variance."""
    values = [quantity, multiplier, sigma_s, sigma_f, rho]
    if not all(isfinite(x) for x in values):
        raise ValueError("Parameters must be finite")
    if quantity <= 0 or multiplier <= 0 or sigma_s < 0 or sigma_f <= 0:
        raise ValueError(
            "Need positive exposure/multiplier/futures volatility"
        )
    if not -1 <= rho <= 1:
        raise ValueError("Correlation outside [-1,1]")
    covariance = rho * sigma_s * sigma_f
    h = covariance / sigma_f**2
    optimum = quantity * h / multiplier

    def variance(n_s):
        # Completed-square form avoids catastrophic cancellation near |rho|=1.
        return (
            quantity**2 * sigma_s**2 * (1 - rho**2) +
            multiplier**2 * sigma_f**2 * (n_s - optimum) ** 2
        )

    candidates = [floor(optimum), floor(optimum) + 1]
    integer = min(candidates, key=variance)
    return h, optimum, integer, variance


def variance(values):
    mu = sum(values) / len(values)
    return sum((x - mu) ** 2 for x in values) / len(values)


def main():
    h, n_s, rounded, risk = sizing(230_000, 25_000, 2, 2.5, 0.8)
    assert isclose(h, 0.64) and isclose(n_s, 5.888) and rounded == 6
    assert risk(6) < risk(5) and risk(6) < risk(7)
    residual_variance = 230_000**2 * 2**2 * (1 - 0.8**2)
    assert isclose(risk(n_s), residual_variance)
    assert isclose(risk(6) - risk(n_s), (25_000 * 2.5) ** 2 * (6 - n_s) ** 2)
    assert sizing(230_000, 25_000, 2, 2.5, -0.8)[1] < 0
    # The source example's 0.8 correlation leaves 36% of variance, not 20%.
    assert isclose(1 - 0.8**2, 0.36)
    x, error = [-2, -1, 1, 2], [1, -1, -1, 1]
    train = [0.8 * a + e for a, e in zip(x, error)]
    changed = [-0.2 * a + e for a, e in zip(x, error)]
    train_hedged = [y - 0.8 * a for y, a in zip(train, x)]
    changed_hedged = [y - 0.8 * a for y, a in zip(changed, x)]
    assert isclose(variance(train_hedged), 1)
    assert isclose(variance(changed), 1.1)
    assert isclose(variance(changed_hedged), 3.5)
    assert isclose(sqrt(residual_variance), 276_000)
    print(
        f"hedge_ratio={h:.6f}; real_contracts={n_s:.6f}; "
        f"integer_contracts={rounded}"
    )
    print(
        f"unhedged_variance={risk(0):.0f}; "
        f"real_min_variance={risk(n_s):.0f}; "
        f"rounded_variance={risk(rounded):.0f}"
    )
    print(
        f"train_hedged_variance={variance(train_hedged):.6f}; "
        f"changed_unhedged={variance(changed):.6f}; "
        f"changed_hedged={variance(changed_hedged):.6f}"
    )
    print(
        "Projection, integer optimality, correlation signs, "
        "residual-risk fraction and regime-change checks passed."
    )


if __name__ == "__main__":
    main()
