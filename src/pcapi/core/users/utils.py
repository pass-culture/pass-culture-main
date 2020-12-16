from datetime import datetime
from typing import Optional

import jwt

from pcapi import settings
from pcapi.core.users.models import ALGORITHM_HS_256


def create_custom_jwt_token(user_id: int, token_type: str, expiration_date: Optional[datetime] = None) -> str:
    payload = {"userId": user_id, "type": token_type}

    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        payload["exp"] = int(expiration_date.timestamp())
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,  # type: ignore # known as str in build assertion
        algorithm=ALGORITHM_HS_256,
    ).decode("ascii")


def create_jwt_token_with_custom_payload(token_payload: dict, expiration_date: Optional[datetime] = None) -> str:
    payload = token_payload

    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        payload["exp"] = int(expiration_date.timestamp())
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,  # type: ignore # known as str in build assertion
        algorithm=ALGORITHM_HS_256,
    ).decode("ascii")


def format_email(email: str) -> str:
    return email.strip().lower()
