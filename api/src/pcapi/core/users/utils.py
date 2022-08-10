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


def decode_jwt_token_rs256(jwt_token: str) -> dict:
    with open(JWT_ADAGE_PUBLIC_KEY_PATH, "rb") as reader:
        payload = jwt.decode(jwt_token, key=reader.read(), algorithms=[ALGORITHM_RS_256])  # type: ignore # known as str in build assertion
    return payload


def sanitize_email(email: str) -> str:
    return email.strip().lower()


def get_age_at_date(birth_date: date | datetime, specified_datetime: datetime) -> int:
    return max(0, relativedelta(specified_datetime, birth_date).years)


def get_age_from_birth_date(birth_date: date | datetime) -> int:
    return get_age_at_date(birth_date, datetime.utcnow())
