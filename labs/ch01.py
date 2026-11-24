"""Finite certificates; no filesystem, network, or trading effects."""
from math import exp, isclose, isfinite


def costs(rates, quantity, delivery, premium, growth=1.0):
    """Return invoice, forward-hedged, and call-hedged positive costs."""
    rates = list(rates)
    if not rates:
        raise ValueError("Need at least one scenario")
    values = [*rates, quantity, delivery, premium, growth]
    if not all(isfinite(x) for x in values):
        raise ValueError("Inputs must be finite")
    if quantity <= 0 or delivery < 0 or premium < 0 or growth <= 0:
        raise ValueError("Invalid quantity, delivery, premium, or growth")
    if any(x < 0 for x in rates):
        raise ValueError("Exchange rates must be nonnegative")
    invoice = [quantity * x for x in rates]
    forward = [quantity * (x - (x - delivery)) for x in rates]
    option = [quantity * (x - max(x - delivery, 0) + premium * growth)
              for x in rates]
    return invoice, forward, option


def settlements(quotes, quantity):
    """Return simple MTM receipts, cumulative balances, and peak deficit."""
    if len(quotes) < 2 or quantity <= 0:
        raise ValueError("Need at least two quotes and positive quantity")
    if not all(isfinite(x) for x in [*quotes, quantity]):
        raise ValueError("Inputs must be finite")
    flows = [quantity * (b - a) for a, b in zip(quotes, quotes[1:])]
    balances = []
    running = 0.0
    for flow in flows:
        running += flow
        balances.append(running)
    return flows, balances, max(0, -min(balances))


def main():
    rates = [80.0, 86.0, 92.0]
    invoice, forward, option = costs(rates, 100_000, 86, 2)
    assert invoice == [8_000_000, 8_600_000, 9_200_000]
    assert forward == [8_600_000] * 3
    assert option == [8_200_000, 8_800_000, 8_800_000]
    assert costs(iter(rates), 100_000, 86, 2) == (invoice, forward, option)
    try:
        costs([], 100_000, 86, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Empty scenarios accepted")
    # Check the derived identity on both branches and a denser finite grid.
    for rate in [0, 79.5, 85.99, 86, 86.01, 103, 1000]:
        actual = costs([rate], 100_000, 86, 2, exp(0.05 * 0.25))[2][0]
        expected = 100_000 * (min(rate, 86) + 2 * exp(0.0125))
        assert isclose(actual, expected, rel_tol=1e-12)
    flows, balances, deficit = settlements([86, 80, 92, 86], 100_000)
    assert flows == [-600_000, 1_200_000, -600_000]
    assert balances == [-600_000, 600_000, 0]
    assert deficit == 600_000
    assert settlements([86, 70, 86], 100_000)[2] == 1_600_000
    for path in [[86, 80, 92, 86], [86, 92, 80, 86], [86, 70, 86]]:
        total = sum(settlements(path, 100_000)[0])
        assert total == 100_000 * (path[-1] - path[0])
    a, b = [80, 120], [120, 80]
    for vector in [a, b]:
        assert sum(vector) / 2 == 100
        assert sum((x - 100) ** 2 for x in vector) / 2 == 400
    assert [y - x for x, y in zip(a, b)] == [40, -40]
    for reference in [0, 0.04, 0.07, 0.12]:
        loan = 10_000_000 * 0.25 * reference
        swap = 10_000_000 * 0.25 * (reference - 0.06)
        assert isclose(loan - swap, 150_000, abs_tol=1e-8)
    partial = [(100_000 - 80_000) * x + 80_000 * 86 for x in rates]
    assert partial == [8_480_000, 8_600_000, 8_720_000]
    for bad in [float("nan"), float("inf"), -1]:
        try:
            costs([bad], 1, 86, 2)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid rate accepted")
    print("invoice:", [int(x) for x in invoice])
    print("forward cost:", [int(x) for x in forward])
    print("call cost:", [int(x) for x in option])
    print("MTM balances:", [int(x) for x in balances])
    print("peak deficit:", int(deficit))
    print("cash-flow, financing, hedge, and moment certificates passed")


if __name__ == "__main__":
    main()
