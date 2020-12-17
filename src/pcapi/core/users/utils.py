from datetime import datetime
from typing import Optional

import jwt

from pcapi import settings
from pcapi.core.users.models import ALGORITHM_HS_256


def create_custom_jwt_token(user_id: int, token_type: str, expiration_date: Optional[datetime] = None) -> str:
    payload = {"userId": user_id, "type": token_type}

    return encode_jwt_payload(payload, expiration_date)


def encode_jwt_payload(token_payload: dict, expiration_date: Optional[datetime] = None) -> str:
    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        token_payload["exp"] = int(expiration_date.timestamp())

    return jwt.encode(
        token_payload,
        settings.JWT_SECRET_KEY,  # type: ignore # known as str in build assertion
        algorithm=ALGORITHM_HS_256,
    ).decode("ascii")


def decode_jwt_token(jwt_token: str) -> dict:
    return jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms=ALGORITHM_HS_256)  # type: ignore # known as str in build assertion


def format_email(email: str) -> str:
    return email.strip().lower()
