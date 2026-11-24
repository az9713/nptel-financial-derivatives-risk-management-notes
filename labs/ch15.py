"""Analyze synthetic European portfolios and optionally regenerate the atlas.

python labs/ch15.py --figure figures/ch15-payoff-atlas.svg
All monetary values are per share. The teaching data use zero interest.
"""

import argparse
from dataclasses import dataclass
from html import escape
from fractions import Fraction
from math import inf, isclose
from pathlib import Path


CALL = {90: 14, 100: 8, 110: 4, 120: 2}
PUT = {strike: premium - 100 + strike for strike, premium in CALL.items()}


@dataclass(frozen=True)
class Portfolio:
    """Signed quantities, with a terminal cash leg and its discount price."""

    stock: float = 0
    cash: float = 0
    calls: tuple = ()
    puts: tuple = ()
    discount: float = 1

    def cost(self):
        if self.discount <= 0:
            raise ValueError("Discount factor must be positive")
        return (100 * self.stock + self.cash * self.discount
                + sum(qty * CALL[strike] for strike, qty in self.calls)
                + sum(qty * PUT[strike] for strike, qty in self.puts))

    def payoff(self, stock):
        if stock < 0:
            raise ValueError("This model requires nonnegative stock prices")
        return (self.stock * stock + self.cash
                + sum(qty * max(stock - strike, 0)
                      for strike, qty in self.calls)
                + sum(qty * max(strike - stock, 0)
                      for strike, qty in self.puts))

    def profit(self, stock):
        return self.payoff(stock) - self.cost() / self.discount

    def slope(self, stock):
        """Derivative inside a strike interval, excluding kink points."""
        return (self.stock
                + sum(qty for strike, qty in self.calls if stock > strike)
                - sum(qty for strike, qty in self.puts if stock < strike))

    def analyze(self):
        """Exact affine-interval extrema and roots, including the tail.

        A flat zero interval is returned separately from isolated roots.
        No sampled upper endpoint is used to infer a finite tail bound.
        """
        knots = sorted({0, *(k for k, _ in self.calls),
                        *(k for k, _ in self.puts)})
        values = [self.profit(stock) for stock in knots]
        lower, upper = min(values), max(values)
        final_slope = self.slope(knots[-1] + 1)
        if final_slope < 0:
            lower = -inf
        if final_slope > 0:
            upper = inf
        roots, flat = set(), []
        for left, right in zip(knots, knots[1:] + [inf]):
            midpoint = left + 1 if right == inf else (left + right) / 2
            slope, value = self.slope(midpoint), self.profit(left)
            if slope == 0:
                if value == 0:
                    flat.append((left, right))
            else:
                root = left - value / slope
                if left - 1e-10 <= root <= right + 1e-10:
                    roots.add(round(max(root, 0), 10))
        return lower, upper, sorted(roots), flat


STRATEGIES = {
    "Covered call 110": Portfolio(stock=1, calls=((110, -1),)),
    "Protective put 90": Portfolio(stock=1, puts=((90, 1),)),
    "Straddle 100": Portfolio(calls=((100, 1),), puts=((100, 1),)),
    "Strangle 90 / 110": Portfolio(calls=((110, 1),), puts=((90, 1),)),
    "Gut strangle 90 / 110": Portfolio(calls=((90, 1),), puts=((110, 1),)),
    "Strip 100": Portfolio(calls=((100, 1),), puts=((100, 2),)),
    "Strap 100": Portfolio(calls=((100, 2),), puts=((100, 1),)),
    "Bull call 100 / 110": Portfolio(calls=((100, 1), (110, -1))),
    "Bear put 90 / 100": Portfolio(puts=((100, 1), (90, -1))),
    "Butterfly 90 / 100 / 110": Portfolio(
        calls=((90, 1), (100, -2), (110, 1))),
    "Box 90 / 110": Portfolio(calls=((90, 1), (110, -1)),
                              puts=((110, 1), (90, -1))),
}


def assert_close(actual, expected):
    assert isclose(actual, expected, abs_tol=1e-9), (actual, expected)


def verify():
    expected = {
        "Covered call 110": (-96, 14, [96]),
        "Protective put 90": (-14, inf, [104]),
        "Straddle 100": (-16, inf, [84, 116]),
        "Strangle 90 / 110": (-8, inf, [82, 118]),
        "Gut strangle 90 / 110": (-8, inf, [82, 118]),
        "Strip 100": (-24, inf, [88, 124]),
        "Strap 100": (-24, inf, [76, 112]),
        "Bull call 100 / 110": (-4, 6, [104]),
        "Bear put 90 / 100": (-4, 6, [96]),
        "Butterfly 90 / 100 / 110": (-2, 8, [92, 108]),
    }
    for name, result in expected.items():
        lower, upper, roots, flat = STRATEGIES[name].analyze()
        assert_close(lower, result[0])
        assert_close(upper, result[1])
        assert roots == result[2], (name, roots)
        assert not flat
        for root in roots:
            assert_close(STRATEGIES[name].profit(root), 0)
        print(f"{name}: min {lower:g}; max {upper:g}; roots {roots}")
    assert STRATEGIES["Box 90 / 110"].analyze() == (
        0, 0, [], [(0, 90), (90, 110), (110, inf)])
    assert_close(STRATEGIES["Box 90 / 110"].cost(), 20)
    naked_short = Portfolio(calls=((100, -1),))
    assert naked_short.analyze()[0] == -inf
    assert naked_short.analyze()[2] == [108]
    assert Portfolio().analyze() == (0, 0, [], [(0, inf)])
    # Exact rational weights preserve the cancellation of the final slope.
    weighted = Portfolio(calls=((90, Fraction(2, 3)), (100, -1),
                                (120, Fraction(1, 3))))
    assert_close(weighted.cost(), 2)
    low, high, roots, flat = weighted.analyze()
    assert_close(low, -2)
    assert_close(high, 14 / 3)
    assert roots == [93, 114] and not flat
    assert weighted.slope(121) == 0
    for stock in (0, 90, 100, 120, 150):
        if stock <= 90 or stock >= 120:
            expected_payoff = 0
        elif stock <= 100:
            expected_payoff = Fraction(2, 3) * (stock - 90)
        else:
            expected_payoff = Fraction(1, 3) * (120 - stock)
        assert weighted.payoff(stock) == expected_payoff
    wrong_weights = Portfolio(calls=((90, 1), (100, -2), (120, 1)))
    assert wrong_weights.cost() == 0
    assert wrong_weights.payoff(150) == -10
    # A tiny genuine slope or constant loss is not an exactly flat zero.
    tiny_stock = Portfolio(stock=1e-14)
    assert tiny_stock.analyze()[2:] == ([100], [])
    assert tiny_stock.profit(101) > 0
    tiny_call = Portfolio(calls=((100, 1e-14),))
    assert tiny_call.analyze()[2:] == ([108], [])
    assert tiny_call.profit(0) < 0

    # Check exact payoff identities in all regions and at every kink.
    points = (0, 81, 90, 92, 99, 100, 108, 110, 130, 1e9)
    covered_cash_put = Portfolio(cash=110, puts=((110, -1),))
    protective_cash_call = Portfolio(cash=90, calls=((90, 1),))
    put_butterfly = Portfolio(puts=((90, 1), (100, -2), (110, 1)))
    bull_call = Portfolio(calls=((90, 1), (110, -1)))
    bull_put = Portfolio(puts=((90, 1), (110, -1)))
    bear_put = Portfolio(puts=((110, 1), (90, -1)))
    assert_close(bull_call.cost() + bear_put.cost(), 20)
    for stock in points:
        assert_close(STRATEGIES["Covered call 110"].profit(stock),
                     covered_cash_put.profit(stock))
        assert_close(STRATEGIES["Protective put 90"].profit(stock),
                     protective_cash_call.profit(stock))
        assert_close(STRATEGIES["Butterfly 90 / 100 / 110"].profit(stock),
                     put_butterfly.profit(stock))
        assert_close(STRATEGIES["Strangle 90 / 110"].profit(stock),
                     STRATEGIES["Gut strangle 90 / 110"].profit(stock))
        assert_close(bull_call.profit(stock), bull_put.profit(stock))
        assert_close(STRATEGIES["Box 90 / 110"].payoff(stock), 20)
    fair_box = 20 * 0.95
    assert_close(fair_box - 18.5, 0.5)
    assert_close(20 - fair_box / 0.95, 0)

    # Calendar: price an unexpired claim, then subtract the expiring leg.
    calendar = []
    for stock in (80, 100, 130):
        remaining = (max(1.2 * stock - 100, 0)
                     + max(0.8 * stock - 100, 0)) / 2
        closing = remaining - max(stock - 100, 0)
        calendar.append((remaining, closing))
    assert calendar == [(0, 0), (10, 10), (30, 0)]
    assert 100 - 80 > 90 - 80  # Dividend European-expiry counterexample.
    print(f"Calendar (long-call value, closing value): {calendar}")
    print("All analytical tail, root, replication, and calendar checks "
          "passed.")


def figure(path):
    """Pure SVG output, deterministically calculated from portfolio methods."""
    names = ["Covered call 110", "Protective put 90", "Straddle 100",
             "Bull call 100 / 110", "Butterfly 90 / 100 / 110", "Box 90 / 110"]
    ranges = [(-105, 25), (-25, 70), (-25, 90), (-6, 8), (-4, 10), (-1, 1)]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" '
             'height="840" viewBox="0 0 760 840" role="img" '
             'aria-labelledby="title desc">',
             '<title id="title">Calculated European option expiry profits'
             '</title>',
             '<desc id="desc">Six panels, synthetic zero-rate prices. '
             'Stock range zero to 160; panel profit ranges differ. '
             'Covered call min -96 max 14; protective put min -14; '
             'straddle min -16; bull call min -4 max 6; '
             'butterfly min -2 max 8; box zero profit.</desc>',
             '<rect width="760" height="840" fill="#111923"/>',
             '<g font-family="Arial,sans-serif" font-size="14" '
             'fill="#e4eaf2">']
    for index, (name, limits) in enumerate(zip(names, ranges)):
        origin_x, origin_y = (index % 2) * 380, (index // 2) * 280
        left, top, width, height = origin_x + 58, origin_y + 55, 298, 168
        low, high = limits

        def x(value):
            return left + value * width / 160

        def y(value):
            return top + (high - value) * height / (high - low)

        parts.append(f'<text x="{origin_x + 18}" y="{origin_y + 25}" '
                     f'font-size="17">{escape(name)}</text>')
        parts.append(f'<text x="{left}" y="{top - 10}">Profit / share</text>')
        for value in (low, 0, high):
            parts.append(f'<path d="M {left} {y(value):.3f} h {width}" '
                         'stroke="#394957" fill="none"/>')
            parts.append(f'<text x="{left - 6}" y="{y(value) + 5:.3f}" '
                         f'text-anchor="end">{value:g}</text>')
        for value in (0, 40, 80, 120, 160):
            parts.append(f'<text x="{x(value):.3f}" y="{top + height + 21}" '
                         f'text-anchor="middle">{value}</text>')
        portfolio = STRATEGIES[name]
        knots = sorted({0, 160, *(k for k, _ in portfolio.calls),
                        *(k for k, _ in portfolio.puts)})
        for value in knots:
            if 0 < value < 160:
                parts.append(f'<path d="M {x(value):.3f} {top} v {height}" '
                             'stroke="#627184" stroke-dasharray="3 5"/>')
        coordinates = " ".join(f'{x(s):.3f},{y(portfolio.profit(s)):.3f}'
                               for s in knots)
        parts.append(f'<polyline points="{coordinates}" fill="none" '
                     'stroke="#6fddc2" stroke-width="3"/>')
        parts.append(f'<text x="{left + width / 2}" y="{top + height + 45}" '
                     'text-anchor="middle">Terminal stock price</text>')
    parts.extend(['</g>', '</svg>'])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure", type=Path)
    args = parser.parse_args()
    verify()
    if args.figure:
        figure(args.figure)
