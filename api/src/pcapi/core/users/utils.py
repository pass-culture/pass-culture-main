from datetime import date
from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
import jwt

from pcapi import settings


logger = logging.getLogger(__name__)
JWT_ADAGE_PUBLIC_KEY_PATH = f"src/pcapi/routes/adage_iframe/public_key/{settings.JWT_ADAGE_PUBLIC_KEY_FILENAME}"


ALGORITHM_HS_256 = "HS256"
ALGORITHM_RS_256 = "RS256"


def encode_jwt_payload(token_payload: dict, expiration_date: datetime | None = None) -> str:
    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        token_payload["exp"] = int(expiration_date.timestamp())

    return jwt.encode(
        token_payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM_HS_256,
    )


def decode_jwt_token(jwt_token: str) -> dict:
    return jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM_HS_256])


def encode_jwt_payload_rs256(
    token_payload: dict,
    private_key: str | bytes,
    expiration_date: datetime | None = None,
) -> str:
    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        token_payload["exp"] = int(expiration_date.timestamp())
    return jwt.encode(token_payload, key=private_key, algorithm=ALGORITHM_RS_256)


def decode_jwt_token_rs256(jwt_token: str, public_key: str | bytes) -> dict:
    return jwt.decode(jwt_token, key=public_key, algorithms=[ALGORITHM_RS_256])


def get_age_at_date(birth_date: date, specified_datetime: datetime) -> int:
    return max(0, relativedelta(specified_datetime, birth_date).years)


def get_age_from_birth_date(birth_date: date) -> int:
    return get_age_at_date(birth_date, datetime.utcnow())


def format_login_location(country_name: str | None, city_name: str | None) -> str | None:
    if city_name:
        return f"{city_name}, {country_name}" if country_name else city_name

    return country_name
