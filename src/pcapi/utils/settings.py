# This file is intended to be helpers for the pcapi.settings
# Please do not import other pcapi modules as it may lead to
# circular imports resulting in environ variables not be loaded.

from typing import Optional


def parse_email_addresses(addresses: Optional[str]) -> list[str]:
    if not addresses:
        return []
    if "," in addresses:
        result = [a.strip() for a in addresses.split(",")]
    elif ";" in addresses:
        result = [a.strip() for a in addresses.split(";")]
    else:
        result = [addresses]

    return [a for a in result if a]
