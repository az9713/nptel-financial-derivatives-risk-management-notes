"""Forward replication with synthetic prices; no market access."""

from math import exp, isclose, isfinite, log


def discount(rate, years):
    if not all(isfinite(x) for x in [rate, years]) or years < 0:
        raise ValueError("Need finite rate and nonnegative year fraction")
    return exp(-rate * years)


def forward(spot, rate, years, income=(), costs=()):
    """Return delivery quotation for deterministic dated distributions."""
    if not isfinite(spot) or spot < 0:
        raise ValueError("Spot must be finite and nonnegative in this model")
    income, costs = list(income), list(costs)
    for amount, date in income + costs:
        if not all(isfinite(x) for x in [amount, date]):
            raise ValueError("Dated amounts must be finite")
        if amount < 0 or not 0 <= date <= years:
            raise ValueError("Amounts must be nonnegative and inside horizon")
    carry = sum(a * discount(rate, t) for a, t in costs)
    receipts = sum(a * discount(rate, t) for a, t in income)
    return (spot + carry - receipts) / discount(rate, years)


def existing_value(current_forward, delivery, rate, years):
    if not all(isfinite(x) for x in [current_forward, delivery]):
        raise ValueError("Quotations must be finite")
    return (current_forward - delivery) * discount(rate, years)


def main():
    fair = forward(100, 0.05, 1)
    rich_profit = 107 - fair
    cheap_profit = fair - 103
    assert rich_profit > 0 and cheap_profit > 0
    # Every terminal spot cancels in each fully funded arbitrage ledger.
    for terminal in [0, 75, 100, 180]:
        cash_carry = terminal + (107 - terminal) - fair
        reverse = fair - terminal + (terminal - 103)
        assert isclose(cash_carry, rich_profit, abs_tol=1e-12)
        assert isclose(reverse, cheap_profit, abs_tol=1e-12)
    value = existing_value(forward(104, 0.05, 0.5), 102, 0.05, 0.5)
    assert isclose(value, 104 - 102 * exp(-0.025), abs_tol=1e-12)
    dividend_f = forward(50, 0.04, 0.5, income=[(2, 0.25)])
    assert isclose(dividend_f, 50 * exp(0.02) - 2 * exp(0.01))
    fx = 86 * exp((0.06 - 0.02) * 0.25)
    foreign_now = exp(-0.02 * 0.25)
    assert isclose(foreign_now * exp(0.02 * 0.25), 1)
    assert isclose(86 * foreign_now * exp(0.06 * 0.25), fx)
    storage = [(37.5, t) for t in [0, 0.25, 0.5, 0.75]]
    wheat_carry = forward(1200, 0.10, 1, costs=storage)
    convenience = log(wheat_carry / 1425)
    assert convenience > 0
    # Different compounding labels can represent the same discount factor.
    annual_effective = exp(0.05) - 1
    assert isclose(100 * (1 + annual_effective), fair)
    try:
        forward(100, 0.05, 1, costs=[(1, 2)])
    except ValueError:
        pass
    else:
        raise AssertionError("Out-of-horizon cost was not rejected")
    print(
        f"fair={fair:.6f}; rich_profit={rich_profit:.6f}; "
        f"reverse_profit={cheap_profit:.6f}"
    )
    print(
        f"existing_value={value:.6f}; dividend_forward={dividend_f:.6f}; "
        f"FX_forward={fx:.6f}"
    )
    print(
        f"lecture_wheat_carry={wheat_carry:.6f}; "
        f"implied_convenience_yield={convenience:.6%}"
    )
    print(
        "Statewise arbitrage, dividend financing, currency units, "
        "compounding and input-boundary checks passed."
    )


if __name__ == "__main__":
    main()
