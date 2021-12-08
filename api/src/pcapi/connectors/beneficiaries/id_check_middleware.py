import logging

import requests
from simplejson.errors import JSONDecodeError

from pcapi import settings


class IdCheckMiddlewareException(Exception):
    pass


logger = logging.getLogger(__name__)


def ask_for_identity_document_verification(email: str, identity_document: bytes) -> tuple[bool, str]:
    uri = "/simple-registration-process"
    response = requests.post(
        f"{settings.ID_CHECK_MIDDLEWARE_DOMAIN}{uri}",
        headers={
            "X-Authentication": settings.ID_CHECK_MIDDLEWARE_TOKEN,
        },
        data={"email": email},
        files=[("file", identity_document)],
    )

    if response.status_code != 200 and response.status_code != 400:
        try:
            response_data = {"error": "Gateway timeout"} if response.status_code == 504 else response.json()
        except JSONDecodeError:
            response_data = {"error": "unknwon error (response data not decodable)"}
        logger.error(  # pylint: disable=logging-fstring-interpolation
            f"Error asking API jouve identity document verification with status code {response.status_code}",
            extra={
                "email": email,
                "response_content": response_data,
                "jouve_reference": response.headers.get("dossier-reference"),
            },
        )
        raise IdCheckMiddlewareException(
            f"Error asking API jouve identity document verification for email {email}",
        )

    logger.info(
        "Jouve identity document verification",
        extra={
            "jouve_reference": response.headers.get("dossier-reference"),
            "mfiles_id": response.headers.get("ged-user-id"),
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "error": response.json().get("code", ""),
            "email": email,
        },
    )

    return response.status_code == 200, response.json().get("code", "")
