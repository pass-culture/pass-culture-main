# This file is intended to be helpers for the pcapi.settings
# Please do not import other pcapi modules as it may lead to
# circular imports resulting in environ variables not be loaded.
import logging
from typing import Optional


logger = logging.getLogger(__name__)


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


def parse_phone_numbers(phone_numbers: Optional[str]) -> list[str]:
    """expects a string with format like 'name:3360102030405;name:3360102030405'"""

    if not phone_numbers:
        return []
    try:
        return [name_and_phone.strip().split(":")[1] for name_and_phone in phone_numbers.split(";")]
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception("Error when parsing phone_numbers variable %s: %s", phone_numbers, exception)
        return []
