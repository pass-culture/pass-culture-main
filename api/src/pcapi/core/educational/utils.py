from datetime import datetime
from datetime import timedelta
import hashlib
import logging

import jwt

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.users.utils import ALGORITHM_RS_256
from pcapi.routes.adage_iframe.serialization.adage_authentication import AdageFrontRoles
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def compute_educational_booking_cancellation_limit_date(
    event_beginning: datetime, booking_creation_date: datetime
) -> datetime:
    return max(event_beginning - timedelta(days=30), booking_creation_date)


def get_hashed_user_id(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()


def log_information_for_data_purpose(
    event_name: str,
    user_role: AdageFrontRoles | None,
    user_email: str | None = None,
    extra_data: dict | None = None,
    uai: str | None = None,
) -> None:
    if extra_data is None:
        extra_data = {}

    if user_email is not None:
        user_id = get_hashed_user_id(user_email)
        extra_data["userId"] = user_id

    if uai is not None:
        extra_data["uai"] = uai

    if user_role is not None:
        extra_data["user_role"] = user_role

    logger.info(
        event_name,
        extra={"analyticsSource": "adage", **extra_data},
        technical_message_id="collective_analytics_event",
    )


def create_adage_jwt_fake_valid_token(readonly: bool) -> str:
    with open("tests/routes/adage_iframe/private_keys_for_tests/valid_rsa_private_key", "rb") as reader:
        authenticated_informations = {
            "civilite": "M.",
            "nom": "TEST",
            "prenom": "COMPTE",
            "mail": "compte.test@education.gouv.fr",
            "exp": datetime.utcnow() + timedelta(days=1),
        }
        if not readonly:
            authenticated_informations["uai"] = "0910620E"

        return jwt.encode(
            authenticated_informations,
            key=reader.read().decode(),
            algorithm=ALGORITHM_RS_256,
        )


def get_image_from_url(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code != 200:
        raise educational_exceptions.CantGetImageFromUrl
    return response.content
