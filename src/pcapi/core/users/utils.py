from datetime import datetime
import logging
from typing import Optional

import jwt

from pcapi import settings
from pcapi.core.users.constants import METROPOLE_PHONE_PREFIX
from pcapi.core.users.constants import PHONE_PREFIX_BY_DEPARTEMENT_CODE
from pcapi.core.users.exceptions import UserWithoutPhoneNumberException
from pcapi.core.users.models import ALGORITHM_HS_256
from pcapi.core.users.models import User
from pcapi.domain.postal_code.postal_code import PostalCode


logger = logging.getLogger(__name__)


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


def format_phone_number_with_country_code(user: User) -> str:
    if not user.phoneNumber:
        raise UserWithoutPhoneNumberException()

    if not user.postalCode or (
        PostalCode(user.postalCode)._is_overseas_departement()
        and user.departementCode not in PHONE_PREFIX_BY_DEPARTEMENT_CODE
    ):
        logger.warning(
            "Unknown phone prefix for user %s",
            user,
            extra={"departementCode": user.departementCode, "postalCode": user.postalCode},
        )

    phone_prefix = PHONE_PREFIX_BY_DEPARTEMENT_CODE.get(user.departementCode, METROPOLE_PHONE_PREFIX)

    return phone_prefix + user.phoneNumber[1:]
