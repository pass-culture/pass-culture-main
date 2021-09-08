import decimal
import typing


def to_eurocents(amount_in_euros: typing.Union[decimal.Decimal, float]):
    return int(100 * decimal.Decimal(f"{amount_in_euros}"))
