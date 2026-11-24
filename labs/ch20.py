"""Heat-kernel and Greek checks; no files, network, or trading effects."""

from math import exp, isclose, isfinite, log, pi, sqrt

from scipy.integrate import quad
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


def heat_call(spot, strike, rate, volatility, tau):
    """Integrate transformed initial data, independently of the call CDF."""
    x = log(spot / strike)
    theta = volatility**2 * tau / 2
    kappa = 2 * rate / volatility**2
    a, b = (1 - kappa) / 2, -(kappa + 1)**2 / 4

    def integrand(y):
        base = -(y - x)**2 / (4 * theta)
        return (exp(base + (1 - a) * y) - exp(base - a * y))

    integral = quad(integrand, 0, float("inf"), epsabs=1e-11)[0]
    return strike * exp(a * x + b * theta) * integral / sqrt(4 * pi * theta)


def close(actual, expected, tolerance=1e-7):
    assert isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (
        actual, expected
    )


def numerical_greeks(parameters, put):
    center = value(*parameters, put=put)
    analytical = greeks(*parameters, put=put)
    # Parameter order: spot, strike, rate, volatility, years, yield.
    for index, name, h in ((0, 'delta', .001), (2, 'rho', 1e-5),
                           (3, 'vega', 1e-5), (4, 'theta', 1e-5),
                           (5, 'yield_sensitivity', 1e-5)):
        plus, minus = list(parameters), list(parameters)
        plus[index] += h
        minus[index] -= h
        numerical = (value(*plus, put=put) - value(*minus, put=put)) / (2 * h)
        if name == 'theta':
            numerical = -numerical
        close(numerical, analytical[name])
    plus, minus = list(parameters), list(parameters)
    h = .01
    plus[0] += h
    minus[0] -= h
    gamma = (value(*plus, put=put) - 2 * center
             + value(*minus, put=put)) / h**2
    close(gamma, analytical['gamma'])


def main():
    benchmark = (100, 100, .05, .2, 1, 0)
    for spot in (80, 100, 130):
        close(heat_call(spot, 100, .05, .2, 1), value(spot, 100, .05, .2, 1))
    for parameters in (benchmark, (85, 90, .03, .3, .8, .02)):
        for put in (False, True):
            numerical_greeks(parameters, put)
        call = greeks(*parameters)
        put = greeks(*parameters, put=True)
        spot, strike, rate, sigma, tau, yield_rate = parameters
        asset, debt = spot * exp(-yield_rate * tau), strike * exp(-rate * tau)
        close(call['delta'] - put['delta'], exp(-yield_rate * tau))
        close(call['gamma'], put['gamma'])
        close(call['vega'], put['vega'])
        close(call['rho'] - put['rho'], tau * debt)
        close(call['theta'] - put['theta'], yield_rate * asset - rate * debt)
        for is_put, exposure in ((False, call), (True, put)):
            residual = (exposure['theta'] + .5 * sigma**2 * spot**2
                        * exposure['gamma'] + (rate - yield_rate) * spot
                        * exposure['delta'] - rate * value(*parameters,
                                                           put=is_put))
            close(residual, 0)
    exposure = greeks(*benchmark)
    print("Benchmark Greeks", {k: round(v, 8) for k, v in exposure.items()})
    initial = value(*benchmark)
    exact_change = value(105, *benchmark[1:]) - initial
    linear = 5 * exposure['delta']
    quadratic = linear + .5 * 25 * exposure['gamma']
    assert abs(exact_change - quadratic) < abs(exact_change - linear)
    print(f"Stock +5: exact {exact_change:.8f}, delta {linear:.8f}, "
          f"delta-gamma {quadratic:.8f}")
    close(4000 * exposure['delta'], 2547.322604702476)
    close(4000 * exposure['vega'] * .01, 1500.96138766775)
    straddle_delta = exposure['delta'] + greeks(*benchmark, put=True)['delta']
    close(straddle_delta, .2736613023512382)
    neutral_stock = 100 * exp(-(.05 + .2**2 / 2))
    neutral_call = greeks(neutral_stock, *benchmark[1:])['delta']
    neutral_put = greeks(neutral_stock, *benchmark[1:], put=True)['delta']
    neutral_delta = neutral_call + neutral_put
    close(neutral_delta, 0)
    short_delta = greeks(80, 100, .05, .2, .01)['delta']
    long_delta = greeks(80, 100, .05, .2, 1)['delta']
    assert short_delta < .001 < long_delta
    assert greeks(50, 100, .05, .2, .1, put=True)['theta'] > 0
    threshold = 139.16 * (1 - exp(-.1 * (2 / 12)))
    print(f"Source sufficient dividend threshold {threshold:.8f}")
    for tau in (.01, .0001):
        close(greeks(100, 100, .05, .2, tau)['gamma']
              * 100 * .2 * sqrt(2 * pi * tau),
              exp(-((.05 + .2**2 / 2) * sqrt(tau) / .2)**2 / 2))
    print("All heat-kernel, Greek, parity, PDE, and local-risk checks passed.")


if __name__ == '__main__':
    main()
