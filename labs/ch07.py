"""Synthetic index overlays, scenario arithmetic and carry bounds."""

from math import exp, isclose


def count(value, beta, target, multiplier, quotation, futures_beta=1):
    if value <= 0 or multiplier <= 0 or quotation <= 0 or futures_beta == 0:
        raise ValueError(
            "Need positive value/multiplier/quotation and nonzero futures beta"
        )
    return (target - beta) * value / (multiplier * quotation * futures_beta)


def main():
    assert count(100e6, 1.2, 0.5, 250, 1000) == -280
    assert isclose(count(100e6, 1.2, 1.5, 250, 1000), 120)
    target = count(100e6, 1.2, 0, 250, 1000, 0.95)
    rounded = round(target)
    beta = 1.2 + rounded * 250 * 1000 / 100e6 * 0.95
    assert rounded == -505 and isclose(beta, 0.000625)
    cash = 20000 * (90 - 100)
    derivative = -10 * 250 * (750 - 900)
    factor = 2e6 * 1.1 * (750 - 900) / 900
    residual = cash - factor
    assert isclose(cash + derivative, 175000)
    assert isclose(residual + derivative + factor, 175000)
    g0 = 1500 * exp(0.06 * 4 / 12)
    gh = 1350 * exp(0.06 / 12)
    gain = -6 * 250 * (gh - g0)
    assert gh > 1350
    assert isclose(gain, 260302.660320, rel_tol=0, abs_tol=1e-6)
    initial = 200 * exp(-0.03 / 3)
    fair = initial * exp(0.10 / 3)
    assert isclose(fair, 200 * exp(0.07 / 3))
    # Known discrete dividend, independently specified bid/ask and financing.
    sa, sb, ca, cb, rb, rl, t, u, dividend = (
        101,
        99,
        0.2,
        0.2,
        0.06,
        0.04,
        1,
        0.5,
        2,
    )
    upper = (sa + ca) * exp(rb * t) - dividend * exp(rl * (t - u))
    lower = (sb - cb) * exp(rl * t) - dividend * exp(rb * (t - u))
    assert lower < upper
    sell_forward = upper + 1
    buy_forward = lower - 1
    carry_profit = (
        sell_forward + dividend * exp(rl * (t - u)) - (sa + ca) * exp(rb * t)
    )
    reverse_profit = (
        (sb - cb) * exp(rl * t) - dividend * exp(rb * (t - u)) - buy_forward
    )
    assert isclose(carry_profit, 1) and isclose(reverse_profit, 1)
    print(
        f"Neutral count={target:.6f}; rounded={rounded}; "
        f"residual beta={beta:.6f}"
    )
    print(
        f"Opening futures={g0:.6f}; closure futures={gh:.6f}; "
        f"six-short gain={gain:.6f}"
    )
    print(
        f"Synthetic carry fair={fair:.6f}; rich-forward surplus={210-fair:.6f}"
    )
    print(
        f"Executable lower={lower:.6f}; upper={upper:.6f}; "
        "both outside-bound trade certificates passed."
    )


if __name__ == "__main__":
    main()
