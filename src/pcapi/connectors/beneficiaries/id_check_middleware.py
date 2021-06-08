import logging

import requests

from pcapi import settings


class IdCheckMiddlewareException(Exception):
    pass


logger = logging.getLogger(__name__)


def ask_for_identity_document_verification(email: str, identity_document: bytes) -> None:
    uri = "/simple-registration-process"
    response = requests.post(
        f"{settings.ID_CHECK_MIDDLEWARE_DOMAIN}{uri}",
        headers={
            "X-Authentication": settings.ID_CHECK_MIDDLEWARE_TOKEN,
        },
        data={"email": email},
        files=[("file", identity_document)],
    )
    if response.status_code != 200:
        logger.error(
            "Error asking API jouve identity document verification for email %s with reponse content: %s",
            email,
            response.json(),
        )
        raise IdCheckMiddlewareException(
            f"Error asking API jouve identity document verification for email {email}",
        )
