"""Conversion-factor, delivery-invoice, carry and DV01 examples."""
from math import exp, isclose, isfinite, sqrt


def aligned_price(coupon_rate, periods, yield_rate=0.06):
    """Per-100 coupon-aligned price; annual rate compounded semiannually."""
    if (isinstance(periods, bool) or not isinstance(periods, int)
            or periods < 1):
        raise ValueError("Positive integer period count required")
    if (not all(isfinite(x) for x in (coupon_rate, yield_rate))
            or yield_rate <= -2):
        raise ValueError(
            "Positive period count and positive discount base required")
    coupon = 100 * coupon_rate / 2
    discount = 1 + yield_rate / 2
    return (sum(coupon / discount ** j for j in range(1, periods + 1))
            + 100 / discount ** periods)


def main():
    aligned = aligned_price(0.10, 40) / 100
    quarter_dirty = (4 + aligned_price(0.08, 36)) / sqrt(1.03)
    quarter_cf = (quarter_dirty - 2) / 100
    assert isclose(aligned, 1.462295439, rel_tol=1e-8)
    assert quarter_cf > 1
    futures, scale = 110.0, 1000
    clean, factors, accrued = [91, 102.5, 113.7], [
        0.82, 0.93, 1.03], [0.4, 0.9, 1.1]
    invoices = [(futures * cf + ai) * scale for cf,
                ai in zip(factors, accrued)]
    purchase = [(p + ai) * scale for p, ai in zip(clean, accrued)]
    costs = [p - invoice for p, invoice in zip(purchase, invoices)]
    assert all(isclose(x, y, abs_tol=1e-8)
               for x, y in zip(costs, [800, 200, 400]))
    assert costs.index(min(costs)) == 1
    dirty_forward = (103 - 3 * exp(-0.04 * 0.25)) * exp(0.04 * 0.5)
    quote = (dirty_forward - 1.5) / 0.9
    assert isclose(quote * 0.9 + 1.5, dirty_forward)
    cash_dv01, ctd_dv01, conversion = 3000.0, 75.0, 0.9
    future_dv01 = ctd_dv01 / conversion
    contracts = cash_dv01 / future_dv01
    assert isclose(contracts, 36)
    assert isclose(-cash_dv01 * 10 + contracts * future_dv01 * 10, 0)
    # Quote sensitivity carries today's cash DV01 to delivery first.
    carry_factor = 1.02
    carried_dv01 = carry_factor * ctd_dv01 / conversion
    assert isclose(carried_dv01, 85)
    assert isclose(cash_dv01 / carried_dv01, 35.294117647058826)
    step = 1e-6
    cash_derivative = -ctd_dv01 / 1e-4
    quotes = [(carry_factor * (103000 + cash_derivative * dy - 3000)
               - 1500) / conversion for dy in (-step, step)]
    numerical_dv01 = -(quotes[1] - quotes[0]) / (2 * step) * 1e-4
    assert isclose(numerical_dv01, carried_dv01, rel_tol=1e-10)
    for coupon, periods, rate in ((0.05, 2.5, 0.06), (0.05, True, 0.06),
                                  (float("inf"), 20, 0.06),
                                  (0.05, 20, float("nan"))):
        try:
            aligned_price(coupon, periods, rate)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid bond-price domain accepted")
    for y in [0.02, 0.04, 0.06, 0.08]:
        price = aligned_price(0.05, 20, y)
        step = 1e-5
        derivative = (aligned_price(0.05, 20, y + step) -
                      aligned_price(0.05, 20, y - step)) / (2 * step)
        weights = [j / 2 * 2.5 / (1 + y / 2) ** j for j in range(1, 21)]
        weights[-1] += 10 * 100 / (1 + y / 2) ** 20
        macaulay = sum(weights) / price
        modified = macaulay / (1 + y / 2)
        assert isclose(-derivative, modified * price, rel_tol=1e-7)
    print(f"aligned CF={aligned:.9f}; quarter clean CF={quarter_cf:.9f}")
    print("delivery costs:", [round(x, 6) for x in costs], "; CTD=2")
    print(f"forward dirty={dirty_forward:.9f}; normalized quote={quote:.9f}")
    print(f"future DV01={future_dv01:.9f}; short contracts={contracts:.6f}")
    print("conversion, invoice, carry and sensitivity checks passed")


if __name__ == "__main__":
    main()
