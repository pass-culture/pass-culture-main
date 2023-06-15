import logging
import typing

from urllib3 import exceptions as urllib3_exceptions

from pcapi import settings
from pcapi.core import logging as core_logging
from pcapi.utils import requests
from pcapi.utils.cache import get_from_cache


logger = logging.getLogger(__name__)


def get_jwt_token() -> str:
    TITELIVE_JWT_CACHE_KEY = "api:titelive_jwt:cache"
    TITELIVE_JWT_CACHE_TIMEOUT = 5 * 60  # 5 minutes
    url = f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/{settings.TITELIVE_EPAGINE_API_USERNAME}/token"
    payload = {"password": settings.TITELIVE_EPAGINE_API_PASSWORD}

    def _get_new_jwt_token() -> str:
        try:
            response = requests.post(url, json=payload)
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
            core_logging.log_for_supervision(
                logger,
                logging.ERROR,
                "Titelive get jwt: Network error",
                extra={
                    "exception": e,
                    "alert": "Titelive error",
                    "error_type": "network",
                    "request_type": "get-jwt",
                },
            )
            raise requests.ExternalAPIException(is_retryable=True) from e

        if not response.ok:
            if 400 <= response.status_code < 500:
                core_logging.log_for_supervision(
                    logger,
                    logging.ERROR,
                    "Titelive get jwt: External error: %s",
                    response.status_code,
                    extra={
                        "alert": "Titelive error",
                        "error_type": "http",
                        "status_code": response.status_code,
                        "request_type": "get-jwt",
                        "response_text": response.text,
                    },
                )
                raise requests.ExternalAPIException(True, {"status_code": response.status_code})

        return response.json()["token"]

    jwt_token = typing.cast(
        str,
        get_from_cache(
            key_template=TITELIVE_JWT_CACHE_KEY,
            retriever=_get_new_jwt_token,
            expire=TITELIVE_JWT_CACHE_TIMEOUT,
            return_type=str,
        ),
    )

    return jwt_token


def get_by_ean13(ean13: str) -> dict[str, typing.Any]:
    url = f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean13}"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(get_jwt_token())}

    try:
        response = requests.get(url, headers=headers)
    except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            "Titelive get by ean 13: Network error",
            extra={
                "exception": e,
                "alert": "Titelive error",
                "error_type": "network",
                "request_type": "get-by-ean13",
            },
        )
        raise requests.ExternalAPIException(is_retryable=True) from e

    if not response.ok:
        if 400 <= response.status_code < 500:
            core_logging.log_for_supervision(
                logger,
                logging.ERROR,
                "Titelive get by ean 13: External error: %s",
                response.status_code,
                extra={
                    "alert": "Titelive error",
                    "error_type": "http",
                    "status_code": response.status_code,
                    "request_type": "get-by-ean13",
                    "response_text": response.text,
                },
            )
            raise requests.ExternalAPIException(True, {"status_code": response.status_code})

    return response.json()
