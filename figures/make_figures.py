"""Generate original SVG figures from the finite models in the reader."""
from html import escape
from math import isclose
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "figures"


def line(x1, y1, x2, y2, color="#9caec3", dash=""):
    pattern = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1.5"{pattern}/>')


def text(x, y, content, color="#e9eff7", size=15, anchor="start"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'text-anchor="{anchor}" font-family="Arial,sans-serif">'
            f'{escape(str(content))}</text>')


def document(title, elements, width=800, height=430):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" role="img">'
            f'<title>{escape(title)}</title>'
            f'<rect width="{width}" height="{height}" rx="10" '
            'fill="#172435"/>' + "".join(elements) + '</svg>\n')


def importer():
    x = lambda value: 85 + (value - 76) * 40
    y = lambda value: 340 - (value - 7.6) * 120
    elements = [text(35, 32, "The same invoice, three terminal cost rules", size=20)]
    for value in [7.6, 8.0, 8.4, 8.8, 9.2, 9.6]:
        yy = y(value)
        elements.extend([line(85, yy, 725, yy, "#3c506a"),
                         text(70, yy + 5, f"{value:.1f}", anchor="end")])
    for value in [76, 80, 84, 88, 92]:
        xx = x(value)
        elements.extend([line(xx, 340, xx, 347),
                         text(xx, 369, value, anchor="middle")])
    rates = list(range(76, 93))
    series = [("#9ac8ff", [r / 10 for r in rates]),
              ("#9bd9c7", [8.6 for _ in rates]),
              ("#f0c58e", [min(r, 86) / 10 + 0.2 for r in rates])]
    for color, values in series:
        points = " ".join(f"{x(r):.2f},{y(v):.2f}"
                          for r, v in zip(rates, values))
        elements.append(f'<polyline points="{points}" fill="none" '
                        f'stroke="{color}" stroke-width="3"/>')
    elements.extend([text(85, 65, "Cost, million rupees"),
                     text(400, 404, "Terminal exchange rate, rupees per dollar",
                          anchor="middle"),
                     text(490, 62, "Unhedged", "#9ac8ff"),
                     text(490, 84, "Forward K=86", "#9bd9c7"),
                     text(490, 106, "Call K=86, premium=2", "#f0c58e")])
    assert isclose(min(92, 86) / 10 + 0.2, 8.8, abs_tol=1e-12)
    return document("Importer cost: quantity 100000 dollars, zero funding rate",
                    elements)


def funding():
    paths = [("#9ac8ff", [0, -0.6, 0.6, 0], "86 → 80 → 92 → 86"),
             ("#f0c58e", [0, -1.6, -0.4, 0], "86 → 70 → 82 → 86")]
    xs = [105, 290, 475, 660]
    y = lambda value: 150 - value * 100
    elements = [text(35, 32, "Equal final settlement can hide unequal funding", size=20)]
    for value in [-1.6, -0.8, 0, 0.8]:
        yy = y(value)
        elements.extend([line(105, yy, 700, yy, "#3c506a"),
                         text(85, yy + 5, f"{value:.1f}", anchor="end")])
    for color, values, label in paths:
        points = " ".join(f"{xx},{y(v):.2f}" for xx, v in zip(xs, values))
        elements.append(f'<polyline points="{points}" fill="none" '
                        f'stroke="{color}" stroke-width="3"/>')
        elements.append(text(385, 365 if color == "#9ac8ff" else 389,
                             label, color))
    for i, xx in enumerate(xs):
        elements.append(text(xx, 343, f"Date {i}", anchor="middle"))
    elements.extend([text(105, 65, "Cumulative receipts, million rupees"),
                     text(105, 405, "100000 units; gains retained; zero funding rate")])
    assert min(paths[0][1]) == -0.6 and min(paths[1][1]) == -1.6
    return document("Cumulative futures cash flows on two synthetic price paths",
                    elements)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "importer-cost.svg").write_text(
        importer(), encoding="utf-8", newline="\n")
    (OUT / "margin-path.svg").write_text(
        funding(), encoding="utf-8", newline="\n")
    print("Computed importer cap=8.8m, forward=8.6m; funding deficits=0.6m/1.6m")


if __name__ == "__main__":
    main()
