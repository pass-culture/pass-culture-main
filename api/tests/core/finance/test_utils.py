import decimal

from pcapi.core.finance import utils


def test_to_eurocents():
    assert utils.to_eurocents(10) == 1000
    assert utils.to_eurocents(10.10) == 1010
    assert utils.to_eurocents(10.12) == 1012
    assert utils.to_eurocents(decimal.Decimal("10")) == 1000
    assert utils.to_eurocents(decimal.Decimal("10.10")) == 1010
    assert utils.to_eurocents(decimal.Decimal("10.12")) == 1012


def test_to_euros():
    assert utils.to_euros(1000) == 10
    assert utils.to_euros(1234) == decimal.Decimal("12.34")
