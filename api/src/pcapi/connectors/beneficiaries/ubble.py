import datetime
import logging
import urllib.parse

import requests

from pcapi import settings
from pcapi.connectors.beneficiaries import exceptions
from pcapi.core.fraud import models as fraud_models


logger = logging.getLogger(__name__)


def configure_session() -> requests.Session:
    session = requests.Session()
    session.auth = (settings.UBBLE_CLIENT_ID, settings.UBBLE_CLIENT_SECRET)
    session.headers.update(
        {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }
    )

    return session


def build_url(path: str) -> str:
    return urllib.parse.urljoin(settings.UBBLE_API_URL, path)


def start_identification(
    user_id: int,
    phone_number: str,
    birth_date: datetime.date,
    first_name: str,
    last_name: str,
    webhook_url: str,
    redirect_url: str,
    face_required: bool,
) -> fraud_models.UbbleIdentificationResponse:
    session = configure_session()

    data = {
        "data": {
            "type": "identifications",
            "attributes": {
                "identification-form": {
                    "external-user-id": user_id,
                    "phone-number": phone_number,
                },
                "reference-data": {
                    "birth-date": datetime.date.strftime(birth_date, "%Y-%m-%d"),
                    "first-name": first_name,
                    "last-name": last_name,
                },
                "webhook": webhook_url,
                "redirect_url": redirect_url,
                "face_required": face_required,
            },
        }
    }

    try:
        response = session.post(build_url("/identifications/"), json=data)
    except IOError as e:
        # Any exception explicitely raised by requests or urllib3 inherits from IOError
        logger.exception("Request error while starting Ubble identification: %s", e, extra={"alert": "Ubble error"})
        raise exceptions.IdentificationServiceUnavailable()

    if not response.ok:
        # https://ubbleai.github.io/developer-documentation/#errors
        logger.error(
            "Error while starting Ubble identification: %s, %s",
            response.status_code,
            response.text,
            extra={"alert": "Ubble error"},
        )
        if response.status_code in (410, 429):
            raise exceptions.IdentificationServiceUnavailable()
        # Other errors should not happen, so keep them different than Ubble unavailable
        raise exceptions.IdentificationServiceError()

    return fraud_models.UbbleIdentificationResponse(**response.json()["data"]["attributes"])
