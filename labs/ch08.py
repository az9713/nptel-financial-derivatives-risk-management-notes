"""Curve prices, bracketed yields and reinvestment scenarios."""

from math import isclose, isfinite


def price(cash, yield_b):
    if yield_b <= -1:
        raise ValueError("Annual yield must exceed -1")
    return sum(c / (1 + yield_b) ** k for k, c in enumerate(cash, 1))


def ytm(cash, bond_price):
    cash = list(cash)
    if (
        not cash
        or not all(isfinite(c) and c >= 0 for c in cash)
        or not any(cash)
        or not isfinite(bond_price)
        or bond_price <= 0
    ):
        raise ValueError(
            "Need positive price and nonnegative nonzero payments"
        )
    lo, hi = -0.99, 1.0
    if price(cash, lo) < bond_price:
        raise ValueError("Price lies outside the chosen lower bracket")
    while price(cash, hi) > bond_price:
        hi = 2 * hi + 1
    for _ in range(160):
        mid = (lo + hi) / 2
        if price(cash, mid) > bond_price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def growth(cash, initial, reinvest):
    n = len(cash)
    wealth = sum(c * (1 + reinvest) ** (n - k) for k, c in enumerate(cash, 1))
    return (wealth / initial) ** (1 / n) - 1


def main():
    p1, p2 = 1 / 1.10, 1 / 1.15**2
    coupon = 1000 * (1 - p2) / (p1 + p2)
    annuity = 1000 / (p1 + p2)
    assert isclose(ytm([coupon, 1000 + coupon], 1000), coupon / 1000)
    ann_y = ytm([annuity, annuity], 1000)
    assert 0.10 < ann_y < coupon / 1000 < 0.15
    curve_price = 650 / 1.08 + 575 / 1.12**2
    alt1 = 1 / 1.085
    alt2 = (curve_price - 650 * alt1) / 575
    assert alt2 > 0
    assert isclose(650 * alt1 + 575 * alt2, curve_price)
    portfolio_y = ytm([21, 121, 115], 200)
    assert not isclose(portfolio_y, 0.105)
    a, b = [10] * 14 + [110], [3] * 14 + [103]
    pa, pb = price(a, 0.06), price(b, 0.061)
    ga, gb = growth(a, pa, 0.09), growth(b, pb, 0.09)
    assert ga > gb
    for cash, initial, yield_b in ((a, pa, 0.06), (b, pb, 0.061)):
        assert isclose(ytm(cash, initial), yield_b)
        assert isclose(growth(cash, initial, yield_b), yield_b)
        for reinvest in (0.01, 0.04, 0.09):
            g = growth(cash, initial, reinvest)
            assert min(reinvest, yield_b) - 1e-12 <= g
            assert g <= max(reinvest, yield_b) + 1e-12
    effective = (100 / 99) ** (365 / 60) - 1
    print(
        f"Par coupon={coupon:.6f}; equal annuity={annuity:.6f}; "
        f"annuity YTM={ann_y:.6f}"
    )
    print(f"Year2 forward={p1/p2-1:.6f}; portfolio YTM={portfolio_y:.6f}")
    print(
        f"Exact prices A={pa:.6f}, B={pb:.6f}; "
        f"9% reinvestment growth A={ga:.6f}, B={gb:.6f}"
    )
    print(f"60-day bill effective annual equivalent={effective:.6f}")
    print(
        "Repricing, uniqueness brackets, curve ambiguity "
        "and growth checks passed."
    )


if __name__ == "__main__":
    main()
