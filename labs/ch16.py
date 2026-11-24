"""Check scaled-walk laws and a hidden-memory example; no network or files."""
from math import comb, cos, erf, exp, isclose, isfinite, sqrt


def walk_law(steps, horizon=1.0, drift=0.04, volatility=0.2):
    """Return the exact binomial endpoint law on its finite support."""
    if not isinstance(steps, int) or steps <= 0:
        raise ValueError("steps must be a positive integer")
    if not all(isfinite(x) for x in [horizon, drift, volatility]):
        raise ValueError("parameters must be finite")
    if horizon <= 0 or volatility < 0:
        raise ValueError("invalid horizon or volatility")
    jump = volatility * sqrt(horizon / steps)
    return [(drift * horizon + (2 * k - steps) * jump,
             comb(steps, k) / 2 ** steps) for k in range(steps + 1)]


def normal_cdf(value):
    return (1 + erf(value / sqrt(2))) / 2


def corrected_error(law, mean, standard_deviation):
    """Largest CDF error at continuity-corrected lattice boundaries."""
    if len(law) < 2 or standard_deviation <= 0:
        raise ValueError("need a nondegenerate lattice")
    spacing = law[1][0] - law[0][0]
    cumulative = 0.0
    errors = []
    for value, probability in law:
        cumulative += probability
        boundary = value + spacing / 2
        approx = normal_cdf((boundary - mean) / standard_deviation)
        errors.append(abs(cumulative - approx))
    return max(errors)


def main():
    four = walk_law(4)
    expected_values = [-0.36, -0.16, 0.04, 0.24, 0.44]
    expected_probabilities = [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16]
    for (value, probability), target, chance in zip(
            four, expected_values, expected_probabilities):
        assert isclose(value, target, abs_tol=1e-14)
        assert probability == chance
    print("four-step endpoint law:",
          [(round(x, 4), p) for x, p in four])
    for steps in [1, 4, 16, 64, 256]:
        law = walk_law(steps)
        mean = sum(x * p for x, p in law)
        variance = sum((x - mean) ** 2 * p for x, p in law)
        assert isclose(sum(p for _, p in law), 1, abs_tol=1e-13)
        assert isclose(mean, 0.04, abs_tol=1e-13)
        assert isclose(variance, 0.04, abs_tol=1e-13)
    # Covariance of two nested walk sums equals the shared increment variance.
    dt, sigma = 0.25, 0.2
    paths = [(a, b, c, d) for a in [-1, 1] for b in [-1, 1]
             for c in [-1, 1] for d in [-1, 1]]
    covariance = sum((sigma * sqrt(dt) * (a + b))
                     * (sigma * sqrt(dt) * (a + b + c + d))
                     for a, b, c, d in paths) / len(paths)
    assert isclose(covariance, sigma ** 2 * 0.5, abs_tol=1e-14)
    two_date_variance = sum(
        (sigma * sqrt(dt) * (2 * a + 2 * b + c + d)) ** 2
        for a, b, c, d in paths) / len(paths)
    assert isclose(two_date_variance, 0.10, abs_tol=1e-14)
    assert isclose(sigma ** 2 * 1.5, 0.06, abs_tol=1e-14)
    # Endpoint characteristic function, checked against finite enumeration.
    frequency = 2.0
    for steps in [4, 64, 256]:
        law = walk_law(steps, drift=0)
        enumerated = sum(cos(frequency * x) * p for x, p in law)
        product = cos(frequency * 0.2 / sqrt(steps)) ** steps
        assert isclose(enumerated, product, abs_tol=1e-13)
        print(f"n={steps}: characteristic={product:.8f}, "
              f"normal={exp(-0.5 * (frequency * 0.2) ** 2):.8f}")
    errors = [corrected_error(walk_law(n), 0.04, 0.2) for n in [4, 64]]
    assert errors[1] < errors[0]
    print("continuity-corrected CDF errors:",
          [round(x, 8) for x in errors])
    # A persistent direction makes position alone non-Markov.
    retention = 0.75
    p_up_after_up_down = 1 - retention
    p_up_after_down_up = retention
    assert p_up_after_up_down != p_up_after_down_up
    assert sum([1 / 2, 1 / 2]) == 1
    print("next-up probabilities at the same position:",
          p_up_after_up_down, p_up_after_down_up)
    for steps in [0, -1, 2.5]:
        try:
            walk_law(steps)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid step count accepted")
    print("normalization, moments, covariance and finite-law checks passed")


if __name__ == "__main__":
    main()
