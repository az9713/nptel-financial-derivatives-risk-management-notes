"""Duration, convexity, local immunization and curve-twist counterexample."""

from math import exp, isclose


def metrics(cash, y):
    if y <= -1 or not cash or any(c < 0 for c in cash):
        raise ValueError("Need a positive cash-flow stream and yield > -1")
    pv = [c / (1 + y) ** k for k, c in enumerate(cash, 1)]
    value = sum(pv)
    if value <= 0:
        raise ValueError("Need positive value")
    duration = sum(k * p for k, p in enumerate(pv, 1)) / value
    convexity = sum(k * (k + 1) * p for k, p in enumerate(pv, 1))
    convexity /= value * (1 + y) ** 2
    return value, duration, duration / (1 + y), convexity


def wealth(cash, y, horizon):
    return sum(c * (1 + y) ** (horizon - k) for k, c in enumerate(cash, 1))


def main():
    cash, y = [12, 12, 12, 12, 112], 0.18
    value, dmac, dmod, convex = metrics(cash, y)
    eps = 1e-4
    up, down = metrics(cash, y + eps)[0], metrics(cash, y - eps)[0]
    derivative = (up - down) / (2 * eps)
    second = (up - 2 * value + down) / eps**2
    assert isclose(derivative, -value * dmod, rel_tol=1e-6)
    assert isclose(second, value * convex, rel_tol=1e-6)
    dv01 = value * dmod * 1e-4
    assert isclose(dv01, (down - up) / 2, rel_tol=1e-6)
    shock = 0.07
    exact = metrics(cash, y + shock)[0]
    linear = value * (1 - dmod * shock)
    quadratic = value * (1 - dmod * shock + convex * shock**2 / 2)
    assert linear < exact < quadratic
    assert abs(quadratic - exact) < abs(linear - exact)

    def third_derivative(rate):
        return -sum(
            k * (k + 1) * (k + 2) * c / (1 + rate)**(k + 3)
            for k, c in enumerate(cash, 1)
        )

    remainder_lower = -third_derivative(y + shock) * shock**3 / 6
    remainder_upper = -third_derivative(y) * shock**3 / 6
    assert remainder_lower <= quadratic - exact <= remainder_upper
    assert isclose(remainder_lower, 0.2607141748736001)
    assert isclose(remainder_upper, 0.4081130974574006)
    w = wealth(cash, y, dmac)
    wup, wdown = wealth(cash, y + eps, dmac), wealth(cash, y - eps, dmac)
    assert abs((wup - wdown) / (2 * eps)) < 1e-4
    assert wup > w and wdown > w
    weights = [c / (1 + y) ** k / value for k, c in enumerate(cash, 1)]
    dispersion = sum(p * (k - dmac) ** 2 for k, p in enumerate(weights, 1))
    assert isclose(
        (wup - 2 * w + wdown) / eps**2,
        w * dispersion / (1 + y) ** 2,
        rel_tol=1e-5,
    )
    for shift in (-0.02, -0.01, 0, 0.01, 0.02):
        surplus = (
            50 * exp(-shift) + 50 * exp(-3 * shift) - 100 * exp(-2 * shift)
        )
        assert surplus >= -1e-12
    twist_asset = 50 * exp(0.01) + 50 * exp(-0.03)
    assert twist_asset < 100
    assert metrics([0, 0, 100], y)[1] == 3
    print(
        f"Price={value:.6f}; Macaulay={dmac:.6f}; "
        f"modified={dmod:.6f}; convexity={convex:.6f}; DV01={dv01:.6f}"
    )
    print(
        f"25% yield price={exact:.6f}; linear={linear:.6f}; "
        f"quadratic={quadratic:.6f}"
    )
    print(
        f"Matched-horizon wealth={w:.6f}; "
        f"twist surplus={twist_asset-100:.6f}"
    )
    print(
        "Derivative, basis-point scale, Taylor and immunization checks passed."
    )


if __name__ == "__main__":
    main()
