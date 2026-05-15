import logging
import re
import unicodedata

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import Function

from pcapi.utils.countries import INSEE_COUNTRIES


logger = logging.getLogger(__name__)

ACCEPTED_CHARS_FOR_NAMES = [" ", "-", ".", ",", "'", "’"]
ACCEPTED_CHARS_FOR_CITY = [" ", "-", "'", "(", ")"]
ACCEPTED_CHARS_FOR_ADDRESS = ACCEPTED_CHARS_FOR_CITY + [".", ",", "’", "°"]
INSEE_COUNTRIES_CODE_SET = {c for c, _ in INSEE_COUNTRIES}


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


def validate_not_empty(value: str, field_name: str) -> None:
    if not value.strip():
        logger.info("Empty value for field: %s", field_name)
        raise ValueError("le champ ne doit pas être vide")


def validate_name(name: str) -> None:
    validate_not_empty(name, "name")
    if not is_latin(name, accepted_chars=ACCEPTED_CHARS_FOR_NAMES):
        logger.info("Invalid value for field name: %s", name)
        raise ValueError("Les champs textuels doivent contenir des caractères latins")


def validate_address(address: str) -> None:
    validate_not_empty(address, "address")
    for char in address:
        if not is_latin(char, accepted_chars=ACCEPTED_CHARS_FOR_ADDRESS) and not char.isnumeric():
            logger.info("Invalid value for field address: %s", address)
            raise ValueError("L'adresse doit contenir des caractères alphanumériques")


def validate_city(city: str) -> None:
    validate_not_empty(city, "city")
    if not is_latin(city, accepted_chars=ACCEPTED_CHARS_FOR_CITY):
        logger.info("Invalid value for field city: %s", city)
        raise ValueError("Le champ city doit contenir des caractères latins")


def validate_postal_code(postal_code: str) -> None:
    if not re.match(r"^\d{5}$", postal_code):
        logger.info("Invalid value for field postal_code: %s", postal_code)
        raise ValueError("Le code postal doit contenir 5 caractères numériques")


def validate_country_cog_code(country_cog_code: str) -> None:
    if country_cog_code not in INSEE_COUNTRIES_CODE_SET:
        logger.info("Invalid value for field country_cog_code: %s", country_cog_code)
        raise ValueError("Le code cog du pays n'existe pas")


def validate_city_cog_code(city_cog_code: str) -> None:
    if not re.match(r"^(?:\d{5}|2[AB]\d{3})$", city_cog_code):
        logger.info("Invalid value for field city_cog_code: %s", city_cog_code)
        raise ValueError("Le code cog de la commune n'est pas valide")


def matching(column: str | sa_orm.Mapped[str | None], search_value: str) -> ColumnElement[bool]:
    return _sanitized_string(column) == _sanitized_string(search_value)


def _sanitized_string(value: str | sa_orm.Mapped[str | None]) -> Function:
    sanitized = sa.func.replace(value, "-", "")
    sanitized = sa.func.replace(sanitized, " ", "")
    sanitized = sa.func.unaccent(sanitized)
    sanitized = sa.func.lower(sanitized)
    return sanitized
