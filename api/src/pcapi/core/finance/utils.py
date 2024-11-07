import datetime
import decimal

from babel import numbers
from flask import Flask
import pytz


ACCOUNTING_TIMEZONE = pytz.timezone("Europe/Paris")
ROUNDING = decimal.ROUND_HALF_UP
# Article D721-2, Code monétaire et financier
# 1000 CFP = 8.38 €
EUR_TO_XPF_RATE = 1000 / 8.38


def to_eurocents(amount_in_euros: decimal.Decimal | float) -> int:
    exponent = decimal.Decimal("0.01")
    # 0.010 to 0.014 -> 0.01
    # 0.015 to 0.019 -> 0.02
    return int(100 * decimal.Decimal(f"{amount_in_euros}").quantize(exponent, ROUNDING))


def to_euros(amount_in_cents: int) -> decimal.Decimal:
    exponent = decimal.Decimal("0.01")
    return decimal.Decimal(amount_in_cents / 100).quantize(exponent)


def euros_to_xpf(amount_in_euros: decimal.Decimal | float) -> int:
    return round_to_integer(decimal.Decimal(amount_in_euros) * decimal.Decimal(EUR_TO_XPF_RATE))


def round_to_integer(amount: decimal.Decimal) -> int:
    """Round to the closest integer.

    >>> round(100.4)
    100
    >>> round(100.5)
    101
    """
    exponent = decimal.Decimal("1")
    return int(amount.quantize(exponent, ROUNDING))


def fr_percentage_filter(decimal_rate: decimal.Decimal) -> str:
    return numbers.format_percent(decimal_rate, locale="fr_FR", decimal_quantization=False)


def fr_currency_filter(cents: int, use_xpf: bool = False) -> str:
    """Returns a localized str without currency symbol"""
    if use_xpf:
        # to_euros changes cents to main currency unit (euro or xpf)
        amount = to_euros(euros_to_xpf(cents))
    else:
        amount = to_euros(cents)
    return numbers.format_decimal(amount, format="#,##0.00", locale="fr_FR")


def fr_currency_opposite_filter(cents: int, use_xpf: bool = False) -> str:
    """Returns a localized str without currency symbol"""
    return fr_currency_filter(-cents, use_xpf)


def install_template_filters(app: Flask) -> None:
    app.jinja_env.filters["fr_percentage"] = fr_percentage_filter
    app.jinja_env.filters["fr_currency"] = fr_currency_filter
    app.jinja_env.filters["fr_currency_opposite"] = fr_currency_opposite_filter


def format_raw_iban_and_bic(raw_data: str) -> str:
    formatted_data = raw_data.upper()
    formatted_data = formatted_data.replace(" ", "").replace("\xa0", "")
    return formatted_data


def get_cutoff_as_datetime(last_day: datetime.date) -> datetime.datetime:
    """Return a UTC datetime object for the first second of the day after
    the requested date (the latter being expressed as a date in the
    CET/CEST timezone).
    """
    next_day = last_day + datetime.timedelta(days=1)
    first_second = datetime.datetime.combine(next_day, datetime.time.min)
    return ACCOUNTING_TIMEZONE.localize(first_second).astimezone(pytz.utc)
