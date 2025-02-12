import logging
import unicodedata


logger = logging.getLogger(__name__)

ACCEPTED_CHARS_FOR_NAMES = [" ", "-", ".", ",", "'", "’"]
ACCEPTED_CHARS_FOR_CITY = [" ", "-", "'", "(", ")"]
ACCEPTED_CHARS_FOR_ADDRESS = [" ", "-", ".", ",", "'", "’"]


def is_latin(s: str, accepted_chars: list[str]) -> bool:
    if s == "":
        return False
    for char in s:
        if char in accepted_chars:
            continue
        try:
            if "LATIN" not in unicodedata.name(char):
                return False
        # if unicodedata.name does not recognize char, it raises a ValueError
        except ValueError:
            return False
    return True


def validate_not_empty(value: str) -> None:
    if not value:
        logger.info("Empty value for field")
        raise ValueError("This field cannot be empty")


def validate_name(name: str) -> None:
    validate_not_empty(name)
    if not is_latin(name, accepted_chars=ACCEPTED_CHARS_FOR_NAMES):
        logger.info("Invalid value for field name: %s", name)
        raise ValueError("Les champs textuels doivent contenir des caractères latins")


def validate_address(address: str) -> None:
    validate_not_empty(address)
    for char in address:
        if not is_latin(char, accepted_chars=ACCEPTED_CHARS_FOR_ADDRESS) and not char.isnumeric():
            logger.info("Invalid value for field address: %s", address)
            raise ValueError("L'adresse doit contenir des caractères alphanumériques")


def validate_city(city: str) -> None:
    validate_not_empty(city)
    if not is_latin(city, accepted_chars=ACCEPTED_CHARS_FOR_CITY):
        logger.info("Invalid value for field city: %s", city)
        raise ValueError("Le champ city doit contenir des caractères latins")
