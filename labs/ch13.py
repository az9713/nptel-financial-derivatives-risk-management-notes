"""European payoff, financed-profit and parity cash-flow certificates."""
from math import exp, isclose, isfinite


def payoffs(spot, strike):
    if not all(isfinite(x) and x >= 0 for x in [spot, strike]):
        raise ValueError("Nonnegative finite stock and strike required")
    return max(spot - strike, 0), max(strike - spot, 0)


def main():
    strike, discount, call_price, put_price, initial = 100, 0.95, 8, 3, 100
    assert isclose(call_price - put_price, initial - strike * discount)
    for spot in [0, 30, 80, 99.999, 100, 100.001, 110, 140, 1000]:
        call, put = payoffs(spot, strike)
        assert isclose(call - put, spot - strike, abs_tol=1e-12)
        assert isclose(call + strike, spot + put)
        call_profit, put_profit = call - call_price / \
            discount, put - put_price / discount
        assert isclose(call_profit + (-call + call_price / discount), 0)
        assert isclose(put_profit + (-put + put_price / discount), 0)
        # Expensive call-and-bond side: buy stock+put, short call+bond.
        assert isclose(spot + put - call - strike, 0)
    call_break_even = strike + call_price / discount
    put_break_even = strike - put_price / discount
    assert isclose(payoffs(call_break_even, strike)[0], call_price / discount)
    assert isclose(payoffs(put_break_even, strike)[1], put_price / discount)
    rich_call = 9
    receipt = rich_call + strike * discount - put_price - initial
    assert receipt == 1
    executable_receipt = 8 + 95 - 4 - 100.5
    assert executable_receipt < 0
    reverse_receipt = 2 + 99.5 - 10 - 95
    assert isclose(executable_receipt, -1.5)
    assert isclose(reverse_receipt, -3.5)
    assert isclose(10 + 95 - 4 - 100.5, .5)
    dividend_pv, call_dividend, put_dividend = 2, 7, 4
    assert (call_dividend - put_dividend
            == initial - dividend_pv - strike * discount)
    for spot in range(0, 201):
        low_call = payoffs(spot, 90)[0]
        high_call = payoffs(spot, 110)[0]
        assert 0 <= low_call - high_call <= 20
        low_put = payoffs(spot, 90)[1]
        high_put = payoffs(spot, 110)[1]
        assert 0 <= high_put - low_put <= 20
    s0, k, rate, maturity = 50, 100, 0.1, 1
    terminal = s0 * exp(rate * maturity)
    deterministic_put = exp(-rate * maturity) * max(k - terminal, 0)
    assert isclose(deterministic_put, k * exp(-rate * maturity) - s0)
    assert deterministic_put < k - s0
    print(
        f"call break-even={call_break_even:.9f}; "
        f"put break-even={put_break_even:.9f}")
    print(f"parity arbitrage initial receipt={receipt:.6f}; final payoff=0")
    print(f"bid-ask adjusted receipt={executable_receipt:.6f}")
    print(f"deterministic European put={deterministic_put:.9f}; intrinsic=50")
    print("payoff, financed profit, strike order and parity checks passed")


if __name__ == "__main__":
    main()
