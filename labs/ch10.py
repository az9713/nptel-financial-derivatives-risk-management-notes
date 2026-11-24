"""Bill-quotation, cash-price, forward-date and settlement certificates."""
from math import exp, isclose, isfinite


def bill_price(face, discount, days, basis=360):
    """Price a zero-coupon bill using an explicitly stated discount basis."""
    if not all(isfinite(x) for x in [face, discount, days, basis]):
        raise ValueError("Inputs must be finite")
    if face <= 0 or days < 0 or basis <= 0 or 1 - discount * days / basis <= 0:
        raise ValueError("Invalid face, time basis, or nonpositive bill price")
    return face * (1 - discount * days / basis)


def investment_rate(discount, days, basis=360):
    if days <= 0:
        raise ValueError("Positive accrual days required for annualized yield")
    price = bill_price(1.0, discount, days, basis)
    return discount / price


def quote_price(face, index, accrual=0.25):
    if not all(isfinite(x) for x in [face, index, accrual]):
        raise ValueError("Inputs must be finite")
    if face <= 0 or accrual <= 0:
        raise ValueError("Positive face and accrual required")
    price = face * (1 - (100 - index) * accrual / 100)
    if price <= 0:
        raise ValueError("Bill quotation implies nonpositive cash price")
    return price


def main():
    face, days, discount = 1_000_000, 90, 0.05
    price = bill_price(face, discount, days)
    rate = investment_rate(discount, days)
    assert price == 987_500
    assert isclose(price * (1 + rate * days / 360), face)
    simple_price = face / (1 + 0.05 * days / 360)
    assert isclose(simple_price, 987654.3209876543)
    assert isclose(rate, 0.05063291139240506)
    assert quote_price(face, 95) == price
    assert isclose(quote_price(face, 94.99) - price, -25)
    assert isclose(quote_price(face, 94.995) - price, -12.5)
    p0t, p0n = 0.98, 0.965
    delivery = face * p0n / p0t
    simple_forward = (face / delivery - 1) / 0.25
    discount_forward = (1 - delivery / face) / 0.25
    assert isclose(delivery * p0t, face * p0n)
    assert isclose(delivery * (1 + simple_forward * 0.25), face)
    assert isclose(bill_price(face, discount_forward, 90), delivery)
    quotes = [95, 94, 95]
    prices = [quote_price(face, q) for q in quotes]
    flows = [b - a for a, b in zip(prices, prices[1:])]
    assert flows == [-2500, 2500]
    financed = flows[0] * exp(0.04 * 0.25) + flows[1]
    assert financed < 0 and isclose(financed, -25.12541771041972)
    dv01 = face * 0.25 * 0.0001
    assert dv01 == 25
    for d in [-0.01, 0, 0.05, 0.15]:
        p = bill_price(face, d, 90)
        r = investment_rate(d, 90)
        assert isclose(p * (1 + r * 0.25), face)
    for invalid in [float("nan"), float("inf"), 5.0]:
        try:
            bill_price(face, invalid, 90)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid or nonpositive price accepted")
    for index in (-300, -400):
        try:
            quote_price(1, index, 0.25)
        except ValueError:
            pass
        else:
            raise AssertionError("Nonpositive quoted cash price accepted")
    assert bill_price(1, 0.05, 0) == 1
    try:
        investment_rate(0.05, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Annualized yield accepted at zero accrual")
    print(f"discount price={price:.6f}; simple-rate price={simple_price:.6f}")
    print(f"investment rate={rate:.9f}; discount-yield DV01={dv01:.6f}")
    print(
        f"forward delivery={delivery:.6f}; "
        f"simple forward={simple_forward:.9f}")
    print(
        f"discount forward={discount_forward:.9f}; "
        f"financed MTM={financed:.6f}")
    print("quotation, conversion, date, sensitivity and funding checks passed")


if __name__ == "__main__":
    main()
