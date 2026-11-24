"""Binomial checks; no files, network, or trading effects."""

from itertools import product
from math import comb, erf, exp, isclose, isfinite, sqrt


def close(actual, expected):
    assert isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-10), (
        actual, expected
    )


def parameters(spot, up, down, growth):
    values = (spot, up, down, growth)
    if not all(isfinite(x) for x in values):
        raise ValueError("Parameters must be finite")
    if not (spot > 0 and 0 < down < growth < up):
        raise ValueError("Require positive spot and 0 < down < growth < up")
    return (growth - down) / (up - down)


def replicate(spot, up, down, growth, high, low):
    """Return cost, shares, and current cash for a one-period claim."""
    q = parameters(spot, up, down, growth)
    delta = (high - low) / (spot * (up - down))
    cash = (up * low - down * high) / (growth * (up - down))
    cost = delta * spot + cash
    close(delta * spot * up + cash * growth, high)
    close(delta * spot * down + cash * growth, low)
    close(cost, (q * high + (1 - q) * low) / growth)
    return cost, delta, cash


def tree(spot, up, down, growth, steps, payoff, exercise=False):
    """Return all layers, indexed by date then number of up moves."""
    q = parameters(spot, up, down, growth)
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
        raise ValueError("steps must be a positive integer")
    layers = [None] * (steps + 1)
    layers[steps] = [
        payoff(spot * up**j * down**(steps - j))
        for j in range(steps + 1)
    ]
    for i in range(steps - 1, -1, -1):
        layer = []
        for j in range(i + 1):
            continuation = (
                q * layers[i + 1][j + 1]
                + (1 - q) * layers[i + 1][j]
            ) / growth
            intrinsic = payoff(spot * up**j * down**(i - j))
            layer.append(max(intrinsic, continuation)
                         if exercise else continuation)
        layers[i] = layer
    return layers


def terminal_sum(spot, up, down, growth, steps, payoff):
    q = parameters(spot, up, down, growth)
    return sum(
        comb(steps, j) * q**j * (1 - q)**(steps - j)
        * payoff(spot * up**j * down**(steps - j))
        for j in range(steps + 1)
    ) / growth**steps


def verify_paths(layers, spot, up, down, growth):
    """Check each rebalance costs current wealth and final wealth matches."""
    steps = len(layers) - 1
    for path in product((0, 1), repeat=steps):
        price, wealth, j = spot, layers[0][0], 0
        for i, move in enumerate(path):
            cost, delta, cash = replicate(
                price, up, down, growth,
                layers[i + 1][j + 1], layers[i + 1][j]
            )
            close(cost, wealth)
            price *= up if move else down
            wealth = delta * price + cash * growth
            j += move
            close(wealth, layers[i + 1][j])


def main():
    s, u, d, growth = 100.0, 1.2, 0.8, 1.05

    def call(price):
        return max(price - 100, 0)
    q = parameters(s, u, d, growth)
    price, delta, cash = replicate(s, u, d, growth, 20, 0)
    close(q, 0.625)
    close(price, 250 / 21)
    close(delta, 0.5)
    close(cash, -800 / 21)
    physical_mean = 0.8 * 120 + 0.2 * 80
    close(physical_mean, 112)
    close(q * 120 + (1 - q) * 80, 105)
    print(f"One-step call {price:.8f}; physical stock mean {physical_mean}")

    layers = tree(s, u, d, growth, 2, call)
    verify_paths(layers, s, u, d, growth)
    close(layers[0][0], terminal_sum(s, u, d, growth, 2, call))
    print(f"Two-step call {layers[0][0]:.8f}; all four paths replicated")
    for steps in (1, 3, 12, 30):
        result = tree(s, u, d, growth, steps, call)[0][0]
        close(result, terminal_sum(s, u, d, growth, steps, call))

    def source_put(price):

        return max(52 - price, 0)
    source_growth = exp(0.05)
    european = tree(50, u, d, source_growth, 2, source_put)
    american = tree(50, u, d, source_growth, 2, source_put, True)
    verify_paths(european, 50, u, d, source_growth)
    close(american[1][0], 12)
    close(american[1][1], european[1][1])
    assert american[0][0] > european[0][0] > 2
    print(f"Source q {parameters(50, u, d, source_growth):.10f}")
    print(f"Source up/down {european[1][1]:.8f}, {european[1][0]:.8f}")
    print(f"Source European {european[0][0]:.8f}")
    print(f"Source exercise-grid value {american[0][0]:.8f}")
    simple_e = tree(50, u, d, growth, 2, source_put)[0][0]
    simple_a = tree(50, u, d, growth, 2, source_put, True)[0][0]
    close(simple_e, 4.251700680272107)
    close(simple_a, 5.136054421768708)

    for strike in (70, 100, 130):
        value = replicate(s, u, d, growth, max(120 - strike, 0),
                          max(80 - strike, 0))[0]
        expected = {70: 100 - 70 / growth, 100: price, 130: 0}[strike]
        close(value, expected)

    # Expanding the same fixed exercise grid cannot reduce its value.
    continuation = european[1]
    q = parameters(50, u, d, source_growth)
    up_only = (q * max(0, continuation[1])
               + (1 - q) * continuation[0]) / source_growth
    close(up_only, european[0][0])
    assert american[0][0] >= up_only

    for a in (0.1, 0.3):
        weights = (a, 0.75 - 2 * a, a + 0.25)
        close(sum(weights), 1)
        close(sum(w * x for w, x in zip(weights, (80, 100, 120))), 105)
        assert min(weights) > 0
        value = 20 * weights[2] / growth
        assert 5 / growth < value < 12.5 / growth
        print(f"Three-state a={a}: call {value:.8f}")

    def cdf(z):

        return (1 + erf(z / sqrt(2))) / 2
    limiting_call = 100 * cdf(0.35) - 100 * exp(-0.05) * cdf(0.15)
    errors = []
    for steps in (40, 160, 640):
        step = 1 / steps
        up, down = exp(0.2 * sqrt(step)), exp(-0.2 * sqrt(step))
        value = tree(100, up, down, exp(0.05 * step), steps, call)[0][0]
        errors.append(abs(value - limiting_call))
        print(f"Diffusion-grid n={steps}: call {value:.8f}")
    assert errors[2] < errors[1] < errors[0]
    assert errors[-1] < 0.004
    close((100 + 120 + 96) / 3 - 100, 16 / 3)
    close(max((100 + 80 + 96) / 3 - 100, 0), 0)
    for args in ((100, 1.2, 0.8, 1.2), (0, 1.2, 0.8, 1.05)):
        try:
            parameters(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid market was accepted")
    print("All binomial and exercise checks passed.")


if __name__ == "__main__":
    main()
