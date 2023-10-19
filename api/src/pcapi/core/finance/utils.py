import datetime
import decimal

from babel import numbers
from flask import Flask
import pytz


ACCOUNTING_TIMEZONE = pytz.timezone("Europe/Paris")
ROUNDING = decimal.ROUND_HALF_UP


def to_eurocents(amount_in_euros: decimal.Decimal | float) -> int:
    exponent = decimal.Decimal("0.01")
    # 0.010 to 0.014 -> 0.01
    # 0.015 to 0.019 -> 0.02
    return int(100 * decimal.Decimal(f"{amount_in_euros}").quantize(exponent, ROUNDING))


def to_euros(amount_in_eurocents: int) -> decimal.Decimal:
    exponent = decimal.Decimal("0.01")
    return decimal.Decimal(amount_in_eurocents / 100).quantize(exponent)


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


def fr_currency_filter(eurocents: int) -> float:
    """Returns a localized str without signing nor currency symbol"""
    amount_in_euros = to_euros(abs(eurocents))
    return numbers.format_decimal(amount_in_euros, format="#,##0.00", locale="fr_FR")


def install_template_filters(app: Flask) -> None:
    app.jinja_env.filters["fr_percentage"] = fr_percentage_filter
    app.jinja_env.filters["fr_currency"] = fr_currency_filter


def format_raw_iban_and_bic(raw_data: str | None) -> str | None:
    if not raw_data:
        return None

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
