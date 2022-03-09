import decimal
import typing

from babel import numbers


def to_eurocents(amount_in_euros: typing.Union[decimal.Decimal, float]) -> int:
    exponent = decimal.Decimal("0.01")
    # 0.010 to 0.014 -> 0.01
    # 0.015 to 0.019 -> 0.02
    rounding = decimal.ROUND_HALF_UP
    return int(100 * decimal.Decimal(f"{amount_in_euros}").quantize(exponent, rounding))


def to_euros(amount_in_eurocents: int) -> decimal.Decimal:
    exponent = decimal.Decimal("0.01")
    return decimal.Decimal(amount_in_eurocents / 100).quantize(exponent)


def fr_percentage_filter(decimal_rate: decimal.Decimal) -> str:
    return numbers.format_percent(decimal_rate, locale="fr_FR", decimal_quantization=False)


def fr_currency_filter(eurocents: int) -> float:
    """Returns a localized str without signing nor currency symbol"""
    amount_in_euros = to_euros(abs(eurocents))
    return numbers.format_decimal(amount_in_euros, format="#,##0.00", locale="fr_FR")


def install_template_filters(app) -> None:
    app.jinja_env.filters["fr_percentage"] = fr_percentage_filter
    app.jinja_env.filters["fr_currency"] = fr_currency_filter


def format_raw_iban_and_bic(raw_data: str) -> typing.Optional[str]:
    if not raw_data:
        return None

    formatted_data = raw_data.upper()
    formatted_data = formatted_data.replace(" ", "")
    return formatted_data
