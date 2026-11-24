"""Rate-hedge decomposition, funding tailing and accrued-interest checks."""
from math import isclose, isfinite, prod


def bill(face, discount, remaining):
    return face * (1 - discount * remaining)


def tailed_stock_hedge(spots, growth):
    """Return terminal wealth under matched deterministic no-income carry."""
    if len(spots) != len(growth) + 1:
        raise ValueError("One growth factor per interval required")
    if any(not isfinite(g) or g <= 0 for g in growth):
        raise ValueError("Finite positive growth factors required")
    if any(not isfinite(s) or s <= 0 for s in spots):
        raise ValueError("Finite positive stock prices required")
    futures = [s * prod(growth[i:]) for i, s in enumerate(spots)]
    cash = 0.0
    for i, g in enumerate(growth):
        cash *= g
        position = -1 / prod(growth[i + 1:])
        cash += position * (futures[i + 1] - futures[i])
    return spots[-1] + cash


def main():
    face, initial, horizon = 10_000_000, 1.0, 1 / 6
    remaining, d0, dh = initial - horizon, 0.04, 0.055
    start = bill(face, d0, initial)
    base = bill(face, d0, remaining)
    end = bill(face, dh, remaining)
    carry, shock = base - start, end - base
    assert isclose(carry, face * d0 * horizon)
    assert isclose(shock, -125_000)
    assert isclose(end - start, carry + shock)
    contract, accrual = 1_000_000, 0.25
    count = face * remaining / (contract * accrual)
    gain = count * contract * accrual * (dh - d0)
    rounded = 33 * contract * accrual * (dh - d0)
    assert isclose(gain + shock, 0, abs_tol=1e-8)
    assert isclose(rounded + shock, -1250)
    basis_residual = count * contract * accrual * 0.01 + shock
    assert isclose(basis_residual, -41666.66666666667)
    principal, investment_accrual, growth = 2_000_000, 0.5, 1.02
    deposit_loss = principal * investment_accrual * 0.01
    tailed = principal * investment_accrual / (contract * accrual * growth)
    gain_at_close = tailed * contract * accrual * 0.01
    assert isclose(gain_at_close * growth, deposit_loss)
    for path in [[100, 80, 120, 95], [100, 110, 90, 130],
                 [100, 100, 100, 100]]:
        factors = [1.01, 1.02, 1.005]
        wealth = tailed_stock_hedge(path, factors)
        assert isclose(wealth, path[0] * prod(factors), abs_tol=1e-10)
    for path in [[100, 70, 140], [100, 110, 85]]:
        assert isclose(tailed_stock_hedge(path, [0.99, 1.01]), 99.99)
    for invalid in (float("nan"), float("inf"), 0, -1):
        for path, factors in (([100, 101], [invalid]),
                              ([100, invalid], [1.01])):
            try:
                tailed_stock_hedge(path, factors)
            except ValueError:
                pass
            else:
                raise AssertionError("Invalid tailing domain accepted")
    coupon, elapsed, period, clean = 3.0, 60, 180, 99.25
    accrued = coupon * elapsed / period
    assert accrued == 1 and clean + accrued == 100.25
    fair = 97.5 / 0.99
    assert isclose(fair, 98.48484848484848)
    assert isclose(99 - fair, 0.5151515151515151)
    print(f"bill carry={carry:.6f}; yield shock={shock:.6f}")
    print(f"contracts={count:.9f}; rounded residual={rounded + shock:.6f}")
    print(f"basis residual={basis_residual:.6f}; tailed count={tailed:.9f}")
    print(f"close gain={gain_at_close:.6f}; terminal gain={deposit_loss:.6f}")
    print(f"accrued={accrued:.6f}; dirty={clean + accrued:.6f}")
    print("carry, basis, tailed path and invoice checks passed")


if __name__ == "__main__":
    main()
