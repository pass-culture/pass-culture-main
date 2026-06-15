import decimal


def float_to_decimal(value: float) -> decimal.Decimal:
    # cast to string before Decimal to avoid rounding errors
    # Decimal(1.99) -> Decimal("1.9899999999999999911182158029987476766109466552734375")
    # Decimal("1.99") -> Decimal("1.99")
    return decimal.Decimal(str(value))
