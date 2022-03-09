import decimal

from pcapi.core.finance import utils


def test_to_eurocents():
    assert utils.to_eurocents(10) == 1000
    assert utils.to_eurocents(10.10) == 1010
    assert utils.to_eurocents(10.12) == 1012
    # Multiple tests for rounding (we want to round, not truncate).
    # Yes, all tests are useful and must be kept because the default
    # method of rounding with `Decimal.quantize()` may not be what you
    # think:
    #     >>> Decimal("7.505").quantize(Decimal("0.01"))
    #     Decimal('7.50')
    #     >>> Decimal("7.515").quantize(Decimal("0.01"))
    #     Decimal('7.52')
    #     >>> Decimal("7.525").quantize(Decimal("0.01"))
    #     Decimal('7.52')
    assert utils.to_eurocents(7.504) == 750
    assert utils.to_eurocents(7.505) == 751
    assert utils.to_eurocents(7.515) == 752
    assert utils.to_eurocents(decimal.Decimal("10")) == 1000
    assert utils.to_eurocents(decimal.Decimal("10.10")) == 1010
    assert utils.to_eurocents(decimal.Decimal("10.105")) == 1011
    assert utils.to_eurocents(decimal.Decimal("10.115")) == 1012
    assert utils.to_eurocents(decimal.Decimal("10.12")) == 1012

    assert utils.to_eurocents(-7.504) == -750
    assert utils.to_eurocents(-7.505) == -751
    assert utils.to_eurocents(-7.515) == -752


def test_to_euros():
    assert utils.to_euros(1000) == 10
    assert utils.to_euros(1234) == decimal.Decimal("12.34")


def test_fr_percentage_filter():
    assert utils.fr_percentage_filter(decimal.Decimal("1.0000")) == "100 %"
    assert utils.fr_percentage_filter(decimal.Decimal("0.0000")) == "0 %"
    assert utils.fr_percentage_filter(decimal.Decimal("0.5000")) == "50 %"
    assert utils.fr_percentage_filter(decimal.Decimal("0.1234")) == "12,34 %"


def test_fr_currency_filter():
    assert utils.fr_currency_filter(0) == "0,00"
    assert utils.fr_currency_filter(-1234) == "12,34"
    assert utils.fr_currency_filter(500000) == "5 000,00"


def test_format_raw_iban_and_bic():
    assert utils.format_raw_iban_and_bic(None) is None
    assert utils.format_raw_iban_and_bic(" Space and Mixed Case  ") == "SPACEANDMIXEDCASE"
