"""Measure-change, pricing, and PDE checks; no filesystem/network effects."""

from math import exp, isclose, isfinite, log, sqrt

from scipy.integrate import quad
from scipy.stats import norm


def close(actual, expected, absolute=2e-9):
    assert isclose(actual, expected, rel_tol=2e-9, abs_tol=absolute), (
        actual, expected
    )


def black_scholes(spot, strike, rate, volatility, tau):
    """Positive spot/strike, nonnegative volatility and remaining years."""
    if not all(isfinite(x) for x in (spot, strike, rate, volatility, tau)):
        raise ValueError("Inputs must be finite")
    if spot <= 0 or strike <= 0 or volatility < 0 or tau < 0:
        raise ValueError("Invalid spot, strike, volatility, or maturity")
    discount = exp(-rate * tau)
    if tau == 0 or volatility == 0:
        call = max(spot - strike * discount, 0)
        put = max(strike * discount - spot, 0)
        return call, put
    width = volatility * sqrt(tau)
    d1 = (log(spot / strike) + (rate + volatility**2 / 2) * tau) / width
    d2 = d1 - width
    call = spot * norm.cdf(d1) - strike * discount * norm.cdf(d2)
    put = strike * discount * norm.cdf(-d2) - spot * norm.cdf(-d1)
    return call, put


def normal_integral(function, low=-12, high=12):
    """Fixed finite integration bounds; tail negligible for parameters used."""
    return quad(lambda z: function(z) * norm.pdf(z), low, high,
                epsabs=1e-10, epsrel=1e-11)[0]


def main():
    spot, strike, rate, mu, sigma, horizon = 100, 100, .05, .12, .2, 1
    lam = (mu - rate) / sigma

    def likelihood(z):
        return exp(-lam * z - lam**2 / 2)

    def physical_stock(z):
        return spot * exp(mu - sigma**2 / 2 + sigma * z)

    def pricing_stock(z):
        return spot * exp(rate - sigma**2 / 2 + sigma * z)
    close(normal_integral(likelihood), 1)
    close(normal_integral(lambda z: likelihood(z) * z), -lam)
    close(normal_integral(lambda z: likelihood(z) * (z + lam)**2), 1)
    close(normal_integral(lambda z: likelihood(z) * physical_stock(z)),
          spot * exp(rate))
    close(normal_integral(pricing_stock), spot * exp(rate))

    call, put = black_scholes(spot, strike, rate, sigma, horizon)
    physical_cut = (log(strike / spot) - mu + sigma**2 / 2) / sigma
    pricing_cut = (log(strike / spot) - rate + sigma**2 / 2) / sigma
    weighted_call = exp(-rate) * normal_integral(
        lambda z: likelihood(z) * (physical_stock(z) - strike), physical_cut
    )
    direct_call = exp(-rate) * normal_integral(
        lambda z: pricing_stock(z) - strike, pricing_cut
    )
    close(weighted_call, call)
    close(direct_call, call)
    close(call - put, spot - strike * exp(-rate))

    d1 = .35
    d2 = .15
    probability = normal_integral(lambda z: 1, pricing_cut)
    truncated = normal_integral(pricing_stock, pricing_cut)
    conditional = truncated / probability
    close(probability, norm.cdf(d2))
    close(truncated, spot * exp(rate) * norm.cdf(d1))
    assert truncated < strike < conditional
    nonexercise = normal_integral(pricing_stock, -12, pricing_cut)
    close(truncated + nonexercise, spot * exp(rate))
    close(nonexercise / (1 - probability),
          spot * exp(rate) * norm.cdf(-d1) / norm.cdf(-d2))
    physical_probability = norm.cdf(-physical_cut)
    assert physical_probability > probability
    print(f"Call {call:.8f}; weighted-physical integral {weighted_call:.8f}")
    print(
        f"Pricing exercise {
            probability:.8f}; physical {
            physical_probability:.8f}")
    print(f"Truncated stock {truncated:.8f}; conditional {conditional:.8f}")

    # Independent differentiation of the price function checks PDE/time sign.
    for price in (80, 100, 130):
        h, ht, tau = .01, 1e-5, .7

        def value(s, t):
            return black_scholes(s, strike, rate, sigma, t)[0]
        center = value(price, tau)
        delta = (value(price + h, tau) - value(price - h, tau)) / (2 * h)
        gamma = (value(price + h, tau) - 2 * center
                 + value(price - h, tau)) / h**2
        calendar_theta = -(value(price, tau + ht)
                           - value(price, tau - ht)) / (2 * ht)
        residual = (calendar_theta + .5 * sigma**2 * price**2 * gamma
                    + rate * price * delta - rate * center)
        assert abs(residual) < 2e-6, residual
        d = (log(price / strike) + (rate + sigma**2 / 2) * tau)
        close(delta, norm.cdf(d / (sigma * sqrt(tau))), absolute=2e-8)
        for physical_drift in (-.2, .12, .4):
            ito_drift = (calendar_theta + physical_drift * price * delta
                         + .5 * sigma**2 * price**2 * gamma)
            hedge_drift = (delta * physical_drift * price
                           + rate * (center - delta * price))
            close(ito_drift, hedge_drift, absolute=2e-6)

    delta = norm.cdf(d1)
    cash = call - delta * spot
    close(cash, -strike * exp(-rate) * norm.cdf(d2))
    for drift in (mu, rate):
        moment2 = spot**2 * exp((2 * drift + sigma**2) * horizon)
        mean = spot * exp(drift * horizon)
        variance = moment2 - mean**2
        close(variance, spot**2 * exp(2 * drift) * (exp(sigma**2) - 1))
        print(f"Price variance at drift {drift}: {variance:.8f}")

    source_z = (log(38 / 40) + (.16 - .35**2 / 2) * .5) / (.35 * sqrt(.5))
    source_probability = norm.cdf(source_z)
    source_put = black_scholes(69, 70, .05, .35, .5)[1]
    close(source_probability, .496907797501081)
    close(source_put, 6.401407649076464)
    print(f"Source physical exercise {source_probability:.8f}")
    print(f"Source put {source_put:.8f}")
    threshold = 100 * (1 - exp(-.05 * .5))
    assert 1 < threshold < 4
    close(black_scholes(100, 100, .05, 0, 1)[0], 100 * (1 - exp(-.05)))
    close(black_scholes(100, 110, .05, .2, 0)[1], 10)
    try:
        black_scholes(100, 100, .05, -.2, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative volatility accepted")
    print("All likelihood, pricing, delta, and PDE checks passed.")


if __name__ == "__main__":
    main()
