import datetime
import decimal

import pytest
import pytz

from pcapi.core.finance import utils


def test_to_eurocents():
    assert utils.to_cents(10) == 1000
    assert utils.to_cents(10.10) == 1010
    assert utils.to_cents(10.12) == 1012
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
    assert utils.to_cents(7.504) == 750
    assert utils.to_cents(7.505) == 751
    assert utils.to_cents(7.515) == 752
    assert utils.to_cents(decimal.Decimal("10")) == 1000
    assert utils.to_cents(decimal.Decimal("10.10")) == 1010
    assert utils.to_cents(decimal.Decimal("10.105")) == 1011
    assert utils.to_cents(decimal.Decimal("10.115")) == 1012
    assert utils.to_cents(decimal.Decimal("10.12")) == 1012

    assert utils.to_cents(-7.504) == -750
    assert utils.to_cents(-7.505) == -751
    assert utils.to_cents(-7.515) == -752


def test_to_euros():
    assert utils.cents_to_full_unit(1000) == 10
    assert utils.cents_to_full_unit(1234) == decimal.Decimal("12.34")


def test_euros_to_xpf():
    assert utils.euros_to_xpf(decimal.Decimal("1")) == 120
    assert utils.euros_to_xpf(decimal.Decimal("9.99")) == 1190
    assert utils.euros_to_xpf(decimal.Decimal("10")) == 1195
    assert utils.euros_to_xpf(decimal.Decimal("10.03")) == 1195
    assert utils.euros_to_xpf(decimal.Decimal("10.04")) == 1200
    assert utils.euros_to_xpf(decimal.Decimal("167.58")) == 20000
    assert utils.euros_to_xpf(decimal.Decimal("167.6")) == 20000


def test_fr_percentage_filter():
    assert utils.fr_percentage_filter(decimal.Decimal("1.0000")) == "100 %"
    assert utils.fr_percentage_filter(decimal.Decimal("0.0000")) == "0 %"
    assert utils.fr_percentage_filter(decimal.Decimal("0.5000")) == "50 %"
    assert utils.fr_percentage_filter(decimal.Decimal("0.1234")) == "12,34 %"


def test_fr_currency_filter():
    assert utils.fr_currency_filter(0) == "0,00"
    assert utils.fr_currency_filter(-1234) == "-12,34"
    assert utils.fr_currency_filter(500000) == "5 000,00"


def test_fr_currency_opposite_filter():
    assert utils.fr_currency_opposite_filter(0) == "0,00"
    assert utils.fr_currency_opposite_filter(-1234) == "12,34"
    assert utils.fr_currency_opposite_filter(500000) == "-5 000,00"


def test_format_raw_iban_and_bic():
    assert utils.format_raw_iban_and_bic(" Space and Mixed Case  ") == "SPACEANDMIXEDCASE"
    assert utils.format_raw_iban_and_bic("1234 5678") == "12345678"


@pytest.mark.parametrize(
    "last_day_as_str, expected_result",
    [
        # CET (UTC+1)
        (datetime.date(2020, 12, 31), datetime.datetime(2020, 12, 31, 23, 0, tzinfo=pytz.utc)),
        (datetime.date(2021, 2, 28), datetime.datetime(2021, 2, 28, 23, 0, tzinfo=pytz.utc)),
        # CEST (UTC+2)
        (datetime.date(2021, 3, 31), datetime.datetime(2021, 3, 31, 22, 0, tzinfo=pytz.utc)),
    ],
)
def test_get_cutoff_as_datetime(last_day_as_str, expected_result):
    assert utils.get_cutoff_as_datetime(last_day_as_str) == expected_result
