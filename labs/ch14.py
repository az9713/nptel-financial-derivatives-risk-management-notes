"""Bounds and grid exercise decisions; synthetic data, currency per share."""

from math import exp, isclose, isfinite


def tree_price(spot, strike, up, down, growth, steps, kind, american=False):
    """Replicate backwards; American exercise is restricted to this grid."""
    if (isinstance(steps, bool) or not isinstance(steps, int) or steps < 1):
        raise ValueError("Positive integer step count required")
    if not all(isfinite(x) for x in (spot, strike, up, down, growth)):
        raise ValueError("Finite market parameters required")
    if not (spot >= 0 and strike >= 0):
        raise ValueError("Invalid stock, strike, or number of steps")
    if not (0 < down < growth < up):
        raise ValueError("Require positive state prices: 0 < d < R < u")
    if kind not in ("call", "put"):
        raise ValueError("Unknown option kind")
    weight = (growth - down) / (up - down)

    def exercise(stock):
        return max(stock - strike if kind == "call" else strike - stock, 0)

    values = [exercise(spot * up**j * down**(steps - j))
              for j in range(steps + 1)]
    for level in range(steps - 1, -1, -1):
        previous = []
        for j in range(level + 1):
            continuation = (weight * values[j + 1]
                            + (1 - weight) * values[j]) / growth
            stock = spot * up**j * down**(level - j)
            previous.append(max(exercise(stock), continuation)
                            if american else continuation)
        values = previous
    return values[0]


def main():
    prepaid, strike_cash = 100 * exp(-0.03), 100 * exp(-0.05)
    lower_call = max(prepaid - strike_cash, 0)
    assert isclose(prepaid, 97.04455335485082)
    assert isclose(lower_call, 1.921610904779417, abs_tol=1e-10)
    assert isclose(100 * exp(0), 100)
    for terminal in (0, 50, 99, 100, 101, 1000):
        call, put = max(terminal - 100, 0), max(100 - terminal, 0)
        assert 0 <= call <= terminal
        assert 0 <= put <= 100
        assert call + 100 >= terminal
        assert put + terminal >= 100
        assert isclose(call + 100 - terminal, put)
    assert 100 - 4 - 95 == 1  # Initial receipt below the call bound.

    european_put = tree_price(80, 100, 1.25, 0.8, 1.05, 1, "put")
    american_put = tree_price(80, 100, 1.25, 0.8, 1.05, 1, "put", True)
    q_up = (1.05 - .8) / (1.05 * (1.25 - .8))
    q_down = (1.25 - 1.05) / (1.05 * (1.25 - .8))
    assert q_up > 0 and q_down > 0
    assert isclose(q_up + q_down, 1 / 1.05)
    assert isclose(100 * q_up + 64 * q_down, 80)
    assert isclose(1.05 * q_up, 5 / 9)
    assert isclose(36 * q_down, european_put)
    assert isclose(european_put, 15.23809523809524)
    assert isclose(american_put, 20)
    assert american_put > european_put
    for spot in (20, 80, 100, 160):
        for steps in (1, 3, 8):
            call = tree_price(spot, 100, 1.2, 0.8, 1.02, steps, "call")
            am_call = tree_price(spot, 100, 1.2, 0.8, 1.02, steps,
                                 "call", True)
            put = tree_price(spot, 100, 1.2, 0.8, 1.02, steps, "put")
            am_put = tree_price(spot, 100, 1.2, 0.8, 1.02, steps,
                                "put", True)
            discount = 1.02**(-steps)
            assert isclose(call, am_call, abs_tol=1e-10)
            assert am_put >= put - 1e-10
            assert spot - 100 - 1e-10 <= am_call - am_put
            assert am_call - am_put <= spot - 100 * discount + 1e-10
            assert am_put <= 100 + 1e-10

    negative_rate_call = 150 - 100 * exp(0.1)
    assert isclose(negative_rate_call, 39.48290819243523)
    assert 150 * exp(-0.1) > 100
    assert negative_rate_call < 150 - 100
    for date in (0, 0.25, 0.5, 1):
        assert 150 - 100 * exp(0.1 * date) <= 50 + 1e-10
    ex_dividend_stock, dividend, strike = 90, 10, 80
    assert max(ex_dividend_stock - strike, 0) == 10
    assert ex_dividend_stock + dividend - strike == 20
    try:
        tree_price(100, 100, 1.1, 0.9, 1.2, 2, "call")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid state-price model was accepted")
    for up, steps in ((1.2, 2.5), (1.2, True), (float("inf"), 2)):
        try:
            tree_price(100, 100, up, 0.8, 1.02, steps, "call")
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid tree input domain accepted")
    print(f"Prepaid share {prepaid:.9f}; call lower bound {lower_call:.9f}")
    print(f"European put {european_put:.9f}; American put {american_put:.9f}")
    print(f"Negative-rate European call {negative_rate_call:.9f}")
    print("All bounds, parity intervals, and exercise assertions passed.")


if __name__ == "__main__":
    main()
