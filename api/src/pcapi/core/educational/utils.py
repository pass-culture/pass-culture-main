import hashlib
import logging
from datetime import datetime
from datetime import timedelta

import jwt
from psycopg2.extras import DateTimeRange

from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational.constants import COLLECTIVE_OFFER_DISPLAYED_STATUS_LABELS
from pcapi.core.users.utils import ALGORITHM_RS_256
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def compute_educational_booking_cancellation_limit_date(
    event_start: datetime, booking_creation_date: datetime
) -> datetime:
    return max(event_start - timedelta(days=30), booking_creation_date)


def get_hashed_user_id(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()


def log_information_for_data_purpose(
    event_name: str,
    user_role: models.AdageFrontRoles | None,
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


UAI_FOR_FAKE_TOKEN = "0910620E"


def create_adage_jwt_fake_valid_token(readonly: bool, can_prebook: bool = True, uai: str | None = None) -> str:
    with open("tests/routes/adage_iframe/private_keys_for_tests/valid_rsa_private_key", "rb") as reader:
        authenticated_informations = {
            "civilite": "M.",
            "nom": "TEST",
            "prenom": "COMPTE",
            "mail": "compte.test@education.gouv.fr",
            "exp": datetime.utcnow() + timedelta(days=1),
            "canPrebook": can_prebook,
        }
        if not readonly:
            authenticated_informations["uai"] = uai if uai is not None else UAI_FOR_FAKE_TOKEN
            authenticated_informations["lat"] = 48.8566  # Paris
            authenticated_informations["lon"] = 2.3522  # Paris

        return jwt.encode(
            authenticated_informations,
            key=reader.read().decode(),
            algorithm=ALGORITHM_RS_256,
        )


def get_image_from_url(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code != 200:
        raise exceptions.CantGetImageFromUrl
    return response.content


def get_non_empty_date_time_range(start: datetime, end: datetime) -> DateTimeRange:
    """
    As the bounds of DateTimeRange are '[)' by default, we need to add 1 second to end to get a non-empty range
    when start and end dates are equal
    """

    if start == end:
        new_end = end + timedelta(seconds=1)
    else:
        new_end = end

    return DateTimeRange(start, new_end)


def get_collective_offer_full_address(offer: models.CollectiveOffer | models.CollectiveOfferTemplate) -> str:
    match offer.locationType:
        case models.CollectiveLocationType.SCHOOL:
            return "En établissement scolaire"

        case models.CollectiveLocationType.ADDRESS:
            assert offer.offererAddress is not None

            address = offer.offererAddress.address.fullAddress

            if offer.offererAddressId == offer.venue.offererAddressId:
                label = offer.venue.common_name
            else:
                label = offer.offererAddress.label

            if label:
                address = f"{label} - {address}"

            return address

        case models.CollectiveLocationType.TO_BE_DEFINED:
            return "À déterminer avec l'enseignant"


def format_collective_offer_displayed_status(
    displayed_status: models.CollectiveOfferDisplayedStatus,
) -> str:
    return COLLECTIVE_OFFER_DISPLAYED_STATUS_LABELS.get(displayed_status) or displayed_status.value
