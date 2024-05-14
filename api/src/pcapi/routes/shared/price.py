from decimal import Decimal


def convert_to_cent(amount: Decimal | None) -> int | None:
    if amount is None:
        return None
    return int(amount * 100)
