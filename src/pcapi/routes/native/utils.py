from decimal import Decimal


def convert_to_cent(amount: Decimal) -> int:
    return int(amount * 100)
