# This file is intended to be helpers for the pcapi.settings
# Please do not import other pcapi modules as it may lead to
# circular imports resulting in environ variables not be loaded.
from typing import List


def parse_email_addresses(addresses: str) -> List[str]:
    if not addresses:
        addresses = []
    elif "," in addresses:
        addresses = [a.strip() for a in addresses.split(",")]
    elif ";" in addresses:
        addresses = [a.strip() for a in addresses.split(";")]
    else:
        addresses = [addresses]

    return [a for a in addresses if a]
