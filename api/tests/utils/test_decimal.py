import decimal

from pcapi.utils.decimal import float_to_decimal


def test_float_to_decimal():
    assert float_to_decimal(1.0) == decimal.Decimal("1")
    assert float_to_decimal(1.5) == decimal.Decimal("1.5")
    assert float_to_decimal(-120.01) == decimal.Decimal("-120.01")
    assert float_to_decimal(1.99) == decimal.Decimal("1.99")
    assert float_to_decimal(1.9999999) == decimal.Decimal("1.9999999")
