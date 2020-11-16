from datetime import datetime
from typing import Optional

import jwt

from pcapi.core.users.models import ALGORITHM_HS_256
from pcapi.flask_app import jwt_secret_key


def create_custom_jwt_token(user_id: int, token_type: str, expiration_date: Optional[datetime] = None) -> str:
    payload = {"userId": user_id, "type": token_type}

    if expiration_date:
        # do not fill exp key if expiration_date is None or jwt.decode would fail
        payload["exp"] = int(expiration_date.timestamp())
    return jwt.encode(
        payload,
        jwt_secret_key,  # type: ignore # known as str in build assertion
        algorithm=ALGORITHM_HS_256,
    ).decode("ascii")
