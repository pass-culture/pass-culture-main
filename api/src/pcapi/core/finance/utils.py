import decimal
import typing


def to_eurocents(amount_in_euros: typing.Union[decimal.Decimal, float]):
    return int(100 * decimal.Decimal(f"{amount_in_euros}"))


def to_euros(amount_in_eurocents: int) -> decimal.Decimal:
    exp = decimal.Decimal("0.01")
    return decimal.Decimal(amount_in_eurocents / 100).quantize(exp)
