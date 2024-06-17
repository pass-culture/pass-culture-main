# This file is intended to be helpers for the pcapi.settings
# Please do not import other pcapi modules as it may lead to
# circular imports resulting in environ variables not be loaded.
import logging
import os


logger = logging.getLogger(__name__)


def parse_str_to_list(content: str | None) -> list[str]:
    if not content:
        return []
    if "," in content:
        result = [a.strip() for a in content.split(",")]
    elif ";" in content:
        result = [a.strip() for a in content.split(";")]
    else:
        result = [content]

    return [a for a in result if a]


def parse_phone_numbers(phone_numbers: str | None) -> list[str]:
    """expects a string with format like 'name:3360102030405;name:3360102030405'"""

    if not phone_numbers:
        return []
    try:
        return [name_and_phone.strip().split(":")[1] for name_and_phone in phone_numbers.split(";")]
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception("Error when parsing phone_numbers variable %s: %s", phone_numbers, exception)
        return []


def env_get_list(key: str, separator: str = ",", type_: type = str) -> list:
    """Return an environment variable as a (possibly empty) list."""

    separated_values = os.environ.get(key, "").strip()
    if not separated_values:
        return []
    return [type_(v) for v in separated_values.split(separator)]
