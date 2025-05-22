from decimal import Decimal
from decimal import InvalidOperation


def format_coordinate(value: str | float | Decimal) -> Decimal:
    try:
        decimal_value = Decimal(value).quantize(Decimal("1.00000"))
    except InvalidOperation as exception:
        raise ValueError("Value cannot be used as coordinate") from exception
    return decimal_value
