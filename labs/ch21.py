"""Greek hedge and financing checks; no files, network, or trading effects."""

from math import exp, isclose, isfinite, log, pi, sqrt

import numpy as np
from scipy.special import ndtr


def value(spot, strike, rate, volatility, tau, yield_rate=0, put=False):
    inputs = (spot, strike, rate, volatility, tau, yield_rate)
    if not all(isfinite(x) for x in inputs):
        raise ValueError("Inputs must be finite")
    if spot <= 0 or strike <= 0 or volatility < 0 or tau < 0:
        raise ValueError("Invalid price, volatility, or remaining time")
    asset = spot * exp(-yield_rate * tau)
    debt = strike * exp(-rate * tau)
    if volatility == 0 or tau == 0:
        return max(debt - asset, 0) if put else max(asset - debt, 0)
    width = volatility * sqrt(tau)
    d1 = (log(spot / strike)
          + (rate - yield_rate + volatility**2 / 2) * tau) / width
    d2 = d1 - width
    if put:
        return debt * ndtr(-d2) - asset * ndtr(-d1)
    return asset * ndtr(d1) - debt * ndtr(d2)


def greeks(spot, strike, rate, volatility, tau, yield_rate=0, put=False):
    value(spot, strike, rate, volatility, tau, yield_rate, put)
    if volatility == 0 or tau == 0:
        raise ValueError(
            "Interior Greeks require positive volatility and time")
    width = volatility * sqrt(tau)
    d1 = (log(spot / strike)
          + (rate - yield_rate + volatility**2 / 2) * tau) / width
    d2 = d1 - width
    asset = spot * exp(-yield_rate * tau)
    debt = strike * exp(-rate * tau)
    density = exp(-d1**2 / 2) / sqrt(2 * pi)
    direction = -1 if put else 1
    n1, n2 = ndtr(direction * d1), ndtr(direction * d2)
    delta = direction * exp(-yield_rate * tau) * n1
    gamma = exp(-yield_rate * tau) * density / (spot * width)
    vega = asset * density * sqrt(tau)
    rho = direction * tau * debt * n2
    yield_sensitivity = -direction * tau * asset * n1
    theta = (-asset * volatility * density / (2 * sqrt(tau))
             + direction * yield_rate * asset * n1
             - direction * rate * debt * n2)
    return dict(delta=delta, gamma=gamma, vega=vega, rho=rho,
                yield_sensitivity=yield_sensitivity, theta=theta)


def solve_hedge(matrix, target):
    """Solve two exposure equations, rejecting ill-conditioned row ratios."""
    matrix, target = np.asarray(matrix, float), np.asarray(target, float)
    if matrix.shape != (2, 2) or target.shape != (2,):
        raise ValueError("Require a 2x2 exposure matrix and two targets")
    if not np.isfinite(matrix).all() or not np.isfinite(target).all():
        raise ValueError("Exposures must be finite")
    row_norm = np.linalg.norm(matrix, axis=1)
    if (row_norm == 0).any():
        raise ValueError("Zero exposure row")
    normalized = matrix / row_norm[:, None]
    if abs(np.linalg.det(normalized)) < 1e-10:
        raise ValueError("Gamma-vega exposure directions are not independent")
    return np.linalg.solve(matrix, target)


def close(actual, expected, tolerance=1e-8):
    assert isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (
        actual, expected
    )


def quadratic_book(price, time):
    return (1_000_000 + 3000 * (price - 90)
            + 400 * (price - 90)**2 - 129600 * time)


def ledger(prices, step=1 / 252):
    """A long quadratic book, short current delta, cash funded to zero."""
    stock = -3000
    cash = -quadratic_book(prices[0], 0) - stock * prices[0]
    for date, price in enumerate(prices[1:], 1):
        wealth_before = quadratic_book(
            price, date * step) + stock * price + cash
        new_stock = -(3000 + 800 * (price - 90))
        trade = new_stock - stock
        cash -= trade * price
        stock = new_stock
        wealth_after = quadratic_book(
            price, date * step) + stock * price + cash
        close(wealth_before, wealth_after)
    return wealth_after


def main():
    close(140 - 200 * .7, 0)
    close(300 - 200 * .6 - 180, 0)
    source_matrix = ((.5, .8), (2, 1.2))
    source_weights = solve_hedge(source_matrix, (5000, 8000))
    close(source_weights[0], 400)
    close(source_weights[1], 6000)
    close(400 * .6 + 6000 * .5 - 3240, 0)
    close(-2000 * .7 - 2000 * (-.3) + 800, 0)

    base = greeks(100, 100, .05, .2, 1)
    hedge1 = greeks(100, 90, .05, .2, .5)
    hedge2 = greeks(100, 110, .05, .2, 1.5)
    matrix = ((hedge1['gamma'], hedge2['gamma']),
              (hedge1['vega'], hedge2['vega']))
    weights = solve_hedge(matrix, (100 * base['gamma'], 100 * base['vega']))
    shares = 100 * base['delta'] - sum(
        w * g['delta'] for w, g in zip(weights, (hedge1, hedge2))
    )
    options = ((-100, 100, 1), (weights[0], 90, .5), (weights[1], 110, 1.5))
    for name in ('gamma', 'vega'):
        close(-100 * base[name] + weights[0] * hedge1[name]
              + weights[1] * hedge2[name], 0)
    close(-100 * base['delta'] + weights[0] * hedge1['delta']
          + weights[1] * hedge2['delta'] + shares, 0)
    cash = -sum(w * value(100, k, .05, .2, t)
                for w, k, t in options) - 100 * shares

    def full_wealth(price, volatility, elapsed=0):
        return (sum(w * value(price, k, .05, volatility, t - elapsed)
                    for w, k, t in options) + shares * price
                + cash * exp(.05 * elapsed))

    # Solve the same hedge independently in gamma contribution coordinates.
    contribution = 50 * base['gamma']
    close(weights[0] * hedge1['gamma'], contribution)
    close(weights[1] * hedge2['gamma'], contribution)
    close(cash, 973.5136837072434)
    close(full_wealth(100, .2), 0)
    net_theta = (sum(w * greeks(100, k, .05, .2, t)['theta']
                     for w, k, t in options) + .05 * cash)
    close(net_theta, 0)
    print("Repricable hedge option amounts", weights, "stock", shares)
    for price, volatility in ((99, .2), (101, .2), (100, .21), (90, .24)):
        print(f"Scenario S={price}, sigma={volatility}: "
              f"funded hedge residual {full_wealth(price, volatility):.8f}")
    assert abs(full_wealth(101, .2)) < .01
    for strike in (90, 110):
        g = greeks(100, strike, .05, .2, 1)
        close(g['vega'] / g['gamma'], 100**2 * .2 * 1)
    same1, same2 = greeks(100, 90, .05, .2, 1), greeks(100, 110, .05, .2, 1)
    try:
        solve_hedge(((same1['gamma'], same2['gamma']),
                     (same1['vega'], same2['vega'])), (1, 3))
    except ValueError:
        pass
    else:
        raise AssertionError("Degenerate same-maturity hedge accepted")
    nearby = greeks(100, 110, .05, .2, .5001)
    large = solve_hedge(((hedge1['gamma'], nearby['gamma']),
                         (hedge1['vega'], nearby['vega'])),
                        (100 * base['gamma'], 100 * base['vega']))
    assert np.linalg.norm(large) > 1000 * np.linalg.norm(weights)

    result = ledger((90, 93, 91))
    close(result, 400 * 13 - 129600 * 2 / 252)
    close(ledger((90, 90, 90)), -129600 * 2 / 252)
    print(
        f"Complete quadratic-book P&L {result:.8f}; "
        "partial stock tranche 3200")
    rate_d, rate_f, tau, exposure = .66, .06, .75, 6.2e6
    foreign_units = exposure * exp(rate_f * tau)
    close(exposure - foreign_units * exp(-rate_f * tau), 0)
    quote_delta = exp((rate_d - rate_f) * tau)
    close(exp(-rate_d * tau) * quote_delta, exp(-rate_f * tau))

    def forward_value(exchange_rate):
        return (exchange_rate * exp(-rate_f * tau)
                - 1.4 * exp(-rate_d * tau))

    step = 1e-5
    numerical_delta = (forward_value(1.25 + step)
                       - forward_value(1.25 - step)) / (2 * step)
    close(numerical_delta, exp(-rate_f * tau))
    print(f"Corrected forward foreign notional {foreign_units:.8f}")
    atm_delta = greeks(100, 100, .1, .25, .5)['delta']
    close(atm_delta, .6447672796293542)
    print(f"Source ATM call delta {atm_delta:.8f}")
    assert greeks(100, 100, .2, .2, 100)[
        'vega'] < greeks(100, 100, .2, .2, 1)['vega']
    gamma_peak = 100 * exp(-(.05 + 1.5 * .2**2))
    vega_peak = 100 * exp(-(.05 - .5 * .2**2))
    for name, peak in (('gamma', gamma_peak), ('vega', vega_peak)):
        central = greeks(peak, 100, .05, .2, 1)[name]
        assert central > greeks(peak - .1, 100, .05, .2, 1)[name]
        assert central > greeks(peak + .1, 100, .05, .2, 1)[name]
    print("All signed hedge, rank, financing, and scenario checks passed.")


if __name__ == '__main__':
    main()
