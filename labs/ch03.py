"""Daily settlement and deterministic-rate replication certificates."""

from math import isclose, isfinite, prod


def margin_ledger(quotes, contracts, multiplier, initial, maintenance):
    if len(quotes) < 2 or not all(
        isfinite(x)
        for x in [*quotes, contracts, multiplier, initial, maintenance]
    ):
        raise ValueError("Need finite inputs and two prices")
    if multiplier <= 0 or not 0 <= maintenance <= initial or initial <= 0:
        raise ValueError("Invalid contract scale or margin thresholds")
    balance = initial
    rows = []
    for old, new in zip(quotes, quotes[1:]):
        flow = contracts * multiplier * (new - old)
        before_call = balance + flow
        call = initial - before_call if before_call < maintenance else 0
        balance = before_call + call
        rows.append((flow, before_call, call, balance))
    return rows


def main():
    prices = [100, 98, 101, 97, 102]
    rows = margin_ledger(prices, 2, 50, 600, 400)
    assert rows == [
        (-200, 400, 0, 400),
        (300, 700, 0, 700),
        (-400, 300, 300, 600),
        (500, 1100, 0, 1100),
    ]
    flows = [r[0] for r in rows]
    calls = sum(r[2] for r in rows)
    profit = rows[-1][-1] - 600 - calls
    assert profit == sum(flows) == 2 * 50 * (102 - 100) == 200
    short_rows = margin_ledger(prices, -2, 50, 600, 400)
    assert sum(r[0] for r in short_rows) == -200
    # Interest-bearing cash flows differ despite the same unweighted sum.
    growth = [1.01, 1.01, 1.01]
    gains = [b - a for a, b in zip([100, 110, 95, 105], [110, 95, 105])]
    factors = [prod(growth[i + 1:]) for i in range(3)]
    held_one_terminal = sum(g * f for g, f in zip(gains, factors))
    scaled_terminal = sum((g / f) * f for g, f in zip(gains, factors))
    assert isclose(scaled_terminal, 5, abs_tol=1e-12)
    assert not isclose(held_one_terminal, 5, abs_tol=1e-8)
    # A two-state pricing model: rate/terminal-price dependence matters.
    probabilities = [0.5, 0.5]
    discounts, spots = [0.9, 1.0], [120, 80]
    mean_d = sum(q * d for q, d in zip(probabilities, discounts))
    mean_s = sum(q * s for q, s in zip(probabilities, spots))
    mean_ds = sum(
        q * d * s for q, d, s in zip(probabilities, discounts, spots)
    )
    forward = mean_ds / mean_d
    covariance = mean_ds - mean_d * mean_s
    assert isclose(forward - mean_s, covariance / mean_d)
    print(
        f"flows={flows}; calls={calls}; final_balance={rows[-1][-1]}; "
        f"trading_profit={profit}"
    )
    print(
        f"one_contract_terminal={held_one_terminal:.6f}; "
        f"scaled_replication_terminal={scaled_terminal:.6f}"
    )
    print(
        f"two_state_forward={forward:.6f}; "
        f"futures_benchmark={mean_s:.6f}; covariance={covariance:.6f}"
    )
    print(
        "Ledger accounting, short signs, threshold boundary, "
        "funded timing and covariance checks passed."
    )


if __name__ == "__main__":
    main()
