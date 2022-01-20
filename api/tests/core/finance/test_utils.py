import decimal

from pcapi.core.finance import utils


def test_to_eurocents():
    assert utils.to_eurocents(10) == 1000
    assert utils.to_eurocents(10.10) == 1010
    assert utils.to_eurocents(10.12) == 1012
    assert utils.to_eurocents(61.098) == 6110  # round, do not truncate
    assert utils.to_eurocents(decimal.Decimal("10")) == 1000
    assert utils.to_eurocents(decimal.Decimal("10.10")) == 1010
    assert utils.to_eurocents(decimal.Decimal("10.12")) == 1012


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
