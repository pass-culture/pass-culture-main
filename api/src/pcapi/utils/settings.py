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
    except Exception as exception:
        logger.exception("Error when parsing phone_numbers variable %s: %s", phone_numbers, exception)
        return []


DATABASE_ALLOWED_SSLMODES = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]


def check_database_ssl_settings(
    sslmode: str | None,
    sslrootcert: str | None,
    sslcert: str | None,
    sslkey: str | None,
) -> None:
    """Raise a ValueError if the database SSL settings are inconsistent."""

    if sslmode and sslmode not in DATABASE_ALLOWED_SSLMODES:
        raise ValueError(f"Invalid DATABASE_SSLMODE: {sslmode}. Allowed values: {', '.join(DATABASE_ALLOWED_SSLMODES)}")

    if sslmode in ("verify-ca", "verify-full"):
        missing_settings = [
            name
            for name, value in (
                ("DATABASE_SSLROOTCERT", sslrootcert),
                ("DATABASE_SSLCERT", sslcert),
                ("DATABASE_SSLKEY", sslkey),
            )
            if not value
        ]
        if missing_settings:
            raise ValueError(
                f"DATABASE_SSLMODE is {sslmode} but these settings are not set: {', '.join(missing_settings)}"
            )

    if bool(sslcert) != bool(sslkey):
        raise ValueError("DATABASE_SSLCERT and DATABASE_SSLKEY must be set together")


def env_get_list(key: str, separator: str = ",", type_: type = str) -> list:
    """Return an environment variable as a (possibly empty) list."""

    separated_values = os.environ.get(key, "").strip()
    if not separated_values:
        return []
    return [type_(v) for v in separated_values.split(separator)]
