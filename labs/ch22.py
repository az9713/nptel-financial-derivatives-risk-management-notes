"""FRA and swap cash-flow checks; no filesystem or network effects."""

from math import exp, isclose, isfinite, log, prod


def close(actual, expected):
    assert isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-8), (
        actual, expected
    )


def forwards(discounts, accruals):
    if len(discounts) != len(accruals) + 1 or not accruals:
        raise ValueError("One accrual per discount-factor interval required")
    if not all(isfinite(x) and x > 0 for x in (*discounts, *accruals)):
        raise ValueError("Discount factors and accruals must be positive")
    return [(discounts[i] / discounts[i + 1] - 1) / delta
            for i, delta in enumerate(accruals)]


def swap_value(notional, fixed_rate, discounts, accruals, projections=None):
    rates = forwards(
        discounts, accruals) if projections is None else projections
    if len(rates) != len(accruals) or not all(isfinite(x) for x in rates):
        raise ValueError("One finite projected rate per payment required")
    return notional * sum(p * delta * (rate - fixed_rate)
                          for p, delta, rate in
                          zip(discounts[1:], accruals, rates))


def main():
    end = 2e6 * .25 * (.05 - .04)
    advance = end / (1 + .25 * .05)
    close(end, 5000)
    close(advance, 4938.271604938272)
    close(advance * (1 + .25 * .05), end)

    # End-paid replication buys bonds with cash released at the reset.
    for reset_bond_price in (.9, 1 / 1.025, 1.01):
        notional, delta, fixed = 2e6, .25, .04
        fixing = (1 / reset_bond_price - 1) / delta
        bought_units = notional / reset_bond_price
        close(bought_units * reset_bond_price, notional)
        terminal = bought_units - notional * (1 + delta * fixed)
        end_coupon = notional * delta * (fixing - fixed)
        advance_coupon = notional * (1 - (1 + delta * fixed)
                                     * reset_bond_price)
        close(terminal, end_coupon)
        close(advance_coupon / reset_bond_price, terminal)
    source_forward = exp(.04 * 3 - .03 * 2) - 1
    source_scenario = 100 * (.06 - source_forward) / (1 + source_forward)
    source_today = 100 * (.06 - source_forward) * exp(-.04 * 3)
    close(source_today, 100 * ((1 + .06) * exp(-.12) - exp(-.06)))
    print(f"Source FRA implied simple forward {source_forward:.10f}")
    print(f"Fixed receiver scenario at 2 years {source_scenario:.8f} million; "
          f"value today {source_today:.8f} million")

    discounts = [1, .98, .955, .925, .89]
    accruals = [.5] * 4
    rates = forwards(discounts, accruals)
    annuity = sum(p * delta for p, delta in zip(discounts[1:], accruals))
    par_rate = (discounts[0] - discounts[-1]) / annuity
    close(annuity, 1.875)
    close(par_rate, .05866666666666666)
    close(swap_value(1e7, par_rate, discounts, accruals), 0)
    original = swap_value(1e7, .06, discounts, accruals)
    close(original, -25000)
    close(swap_value(1e7, .0601, discounts, accruals) - original, -1875)
    weighted_forward = sum(p * delta * f for p, delta, f
                           in zip(discounts[1:], accruals, rates)) / annuity
    close(weighted_forward, par_rate)
    print("Synthetic period forwards", [round(x, 10) for x in rates])
    print(
        f"Synthetic par rate {par_rate:.10f}; "
        f"fixed-payer value {original:.2f}")

    known = [exp(-.04 * .5), exp(-.045), exp(-.048 * 1.5)]
    final_discount = (1 - .05 * .5 * sum(known)) / (1 + .05 * .5)
    zero_rate = -log(final_discount) / 2
    close(sum(2.5 * p for p in known) + 102.5 * final_discount, 100)
    print(
        f"Source bootstrapped P2 {final_discount:.10f}; zero {zero_rate:.10f}")
    floating_bond = 1060 * exp(-.09 * .25)
    wrong_bond = 1030 * exp(-.09 * .25)
    close(floating_bond - wrong_bond, 30 * exp(-.09 * .25))
    print(
        f"Source floating bond {floating_bond:.8f}; "
        f"wrong stub {wrong_bond:.8f}")

    times = [.25, .75, 1.25]
    zero_rates = [.1, .105, .11]
    factors = [exp(-r * t) for r, t in zip(zero_rates, times)]
    fixed_bond = sum(c * p for c, p in zip((4, 4, 104), factors))
    float_bond = 105.1 * factors[0]
    future_rates = forwards(factors, [.5, .5])
    floating_coupons = [5.1] + [100 * .5 * f for f in future_rates]
    strip = sum((4 - c) * p for c, p in zip(floating_coupons, factors))
    close(strip, fixed_bond - float_bond)
    close(strip, -4.267175853140586)
    close(sum(c * p for c, p in zip(floating_coupons, factors))
          + 100 * factors[-1], float_bond)
    print(f"Source receive-fixed bond/strip {strip:.8f} million")
    print("Source later six-month simple rates", future_rates)

    # Deterministic split-curve example; no stochastic basis calibration.
    d, delta, projected = [1, .98, .95], [.5, .5], [.06, .07]
    float_pv = sum(p * a * f for p, a, f in zip(d[1:], delta, projected))
    split_annuity = sum(p * a for p, a in zip(d[1:], delta))
    split_par = float_pv / split_annuity
    close(float_pv, .06265)
    close(split_par, .06492227979274612)
    close(swap_value(1, split_par, d, delta, projected), 0)
    assert not isclose(float_pv, 1 - d[-1])

    for prime in (.05, .12):
        bbb_external, aaa_external = prime + .0075, .065
        bbb_swap_pay, bbb_swap_receive = .0675, prime - .0025
        aaa_swap_pay, aaa_swap_receive = prime - .0025, .065
        bbb_cost = bbb_external + bbb_swap_pay - bbb_swap_receive
        aaa_cost = aaa_external + aaa_swap_pay - aaa_swap_receive
        dealer = (bbb_swap_pay + aaa_swap_pay
                  - bbb_swap_receive - aaa_swap_receive)
        close(bbb_cost, .0775)
        close(aaa_cost, prime - .0025)
        close(dealer, .0025)
        close((.08 - bbb_cost) + (prime - aaa_cost) + dealer, .0075)
    compounded = prod(1 + r * day / 360
                      for r, day in zip((.04, .041, .042), (1, 1, 3))) - 1
    assert compounded > sum(r * day / 360
                            for r, day in zip((.04, .041, .042), (1, 1, 3)))
    close(.05 * 90 / 360, (.05 * 365 / 360) * 90 / 365)
    # Negative forwards are permitted when positive discount factors increase.
    assert forwards([1, 1.01], [.5])[0] < 0
    try:
        forwards([1, 0], [.5])
    except ValueError:
        pass
    else:
        raise AssertionError("Zero discount factor accepted")
    print("All FRA, swap, bootstrap, reset, and funding-ledger checks passed.")


if __name__ == '__main__':
    main()
