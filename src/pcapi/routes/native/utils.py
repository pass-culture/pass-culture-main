from decimal import Decimal
from typing import Optional


def convert_to_cent(amount: Optional[Decimal]) -> Optional[int]:
    if amount is None:
        return None
    return int(amount * 100)
