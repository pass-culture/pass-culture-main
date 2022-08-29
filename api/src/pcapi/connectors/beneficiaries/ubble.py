import logging
import typing
import urllib.parse

from pydantic import networks as pydantic_networks
from requests import exceptions as requests_exceptions
from urllib3 import exceptions as urllib3_exceptions

from pcapi import settings
from pcapi.core import logging as core_logging
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.utils import requests as requests_utils


logger = logging.getLogger(__name__)


def configure_session() -> requests_utils.Session:
    session = requests_utils.Session()
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


INCLUDED_MODELS = {
    "documents": ubble_fraud_models.UbbleIdentificationDocuments,
    "document-checks": ubble_fraud_models.UbbleIdentificationDocumentChecks,
    "reference-data-checks": ubble_fraud_models.UbbleIdentificationReferenceDataChecks,
}


def _get_included_attributes(
    response: ubble_fraud_models.UbbleIdentificationResponse, type_: str
) -> ubble_fraud_models.UbbleIdentificationObject:
    filtered = list(filter(lambda included: included["type"] == type_, response["included"]))  # type: ignore [index]
    attributes = INCLUDED_MODELS[type_](**filtered[0].get("attributes")) if filtered else None
    return attributes


def _get_data_attribute(response: ubble_fraud_models.UbbleIdentificationResponse, name: str) -> typing.Any:
    return response["data"]["attributes"].get(name)  # type: ignore [index]


def _extract_useful_content_from_response(
    response: ubble_fraud_models.UbbleIdentificationResponse,
) -> ubble_fraud_models.UbbleContent:
    documents: ubble_fraud_models.UbbleIdentificationDocuments = _get_included_attributes(response, "documents")  # type: ignore [assignment]
    document_checks: ubble_fraud_models.UbbleIdentificationDocumentChecks = _get_included_attributes(  # type: ignore [assignment]
        response, "document-checks"
    )
    reference_data_checks: ubble_fraud_models.UbbleIdentificationReferenceDataChecks = _get_included_attributes(  # type: ignore [assignment]
        response, "reference-data-checks"
    )

    comment = _get_data_attribute(response, "comment")
    identification_id = _get_data_attribute(response, "identification-id")
    identification_url = _get_data_attribute(response, "identification-url")
    registered_at = _get_data_attribute(response, "created-at")
    processed_at = _get_data_attribute(response, "ended-at")
    score = _get_data_attribute(response, "score")
    status = _get_data_attribute(response, "status")

    content = ubble_fraud_models.UbbleContent(
        birth_date=getattr(documents, "birth_date", None),
        comment=comment,
        document_type=getattr(documents, "document_type", None),
        expiry_date_score=getattr(document_checks, "expiry_date_score", None),
        first_name=getattr(documents, "first_name", None),
        id_document_number=getattr(documents, "document_number", None),
        identification_id=identification_id,
        identification_url=identification_url,
        gender=getattr(documents, "gender", None),
        last_name=getattr(documents, "last_name", None),
        married_name=getattr(documents, "married_name", None),
        ove_score=getattr(document_checks, "ove_score", None),
        reference_data_check_score=getattr(reference_data_checks, "score", None),
        registration_datetime=registered_at,
        processed_datetime=processed_at,
        score=score,
        status=status,
        supported=getattr(document_checks, "supported", None),
        signed_image_front_url=getattr(documents, "signed_image_front_url", None),
        signed_image_back_url=getattr(documents, "signed_image_back_url", None),
    )
    return content


def start_identification(
    user_id: int,
    first_name: str,
    last_name: str,
    webhook_url: str,
    redirect_url: str,
) -> ubble_fraud_models.UbbleContent:
    session = configure_session()

    data = {
        "data": {
            "type": "identifications",
            "attributes": {
                "identification-form": {
                    "external-user-id": user_id,
                    "phone-number": None,
                },
                "reference-data": {
                    "first-name": first_name,
                    "last-name": last_name,
                },
                "webhook": webhook_url,
                "redirect_url": redirect_url,
            },
        }
    }

    try:
        response = session.post(build_url("/identifications/"), json=data)
    except (urllib3_exceptions.HTTPError, requests_exceptions.RequestException) as e:
        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            "Ubble start-identification: Network error",
            extra={
                "exception": e,
                "alert": "Ubble error",
                "error_type": "network",
                "request_type": "start-identification",
            },
        )
        raise requests_utils.ExternalAPIException(is_retryable=True) from e

    if not response.ok:
        # https://ubbleai.github.io/developer-documentation/#errors
        if response.status_code == 429 or response.status_code >= 500:
            core_logging.log_for_supervision(
                logger,
                logging.ERROR,
                "Ubble start-identification: External error: %s",
                response.status_code,
                extra={
                    "alert": "Ubble error",
                    "error_type": "http",
                    "status_code": response.status_code,
                    "request_type": "start-identification",
                    "response_text": response.text,
                },
            )
            raise requests_utils.ExternalAPIException(is_retryable=True)

        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            f"Ubble start-identification: Unexpected error: {response.status_code}, {response.text}",
            extra={
                "alert": "Ubble error",
                "error_type": "http",
                "status_code": response.status_code,
                "request_type": "start-identification",
            },
        )

        raise requests_utils.ExternalAPIException(is_retryable=False)

    content = _extract_useful_content_from_response(response.json())
    core_logging.log_for_supervision(
        logger,
        logging.INFO,
        "Valid response from Ubble",
        extra={
            "status_code": response.status_code,
            "identification_id": str(content.identification_id),
            "request_type": "start-identification",
        },
    )

    logger.info(
        "Ubble identification started",
        extra={"identification_id": str(content.identification_id), "status": str(content.status)},
    )

    return content


def get_content(identification_id: str) -> ubble_fraud_models.UbbleContent:
    session = configure_session()
    base_extra_log = {"request_type": "get-content", "identification_id": identification_id}

    try:
        response = session.get(build_url(f"/identifications/{identification_id}/"))
    except (urllib3_exceptions.HTTPError, requests_exceptions.RequestException) as e:
        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            "Ubble get-content: Network error",
            extra={"exception": e, "error_type": "http"} | base_extra_log,
        )
        raise requests_utils.ExternalAPIException(is_retryable=True) from e

    if not response.ok:
        if response.status_code >= 500 or response.status_code == 429:
            core_logging.log_for_supervision(
                logger,
                logging.ERROR,
                "Ubble get-content: External error: %s",
                response.status_code,
                extra={"response_text": response.text, "error_type": "http", "status_code": response.status_code}
                | base_extra_log,
            )
            raise requests_utils.ExternalAPIException(is_retryable=True)

        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            f"Ubble get-content: Unexpected error: {response.status_code}, {response.text}",  # ungroup errors on sentry
            extra={"response_text": response.text, "status_code": response.status_code, "error_type": "http"}
            | base_extra_log,
        )
        raise requests_utils.ExternalAPIException(is_retryable=False)

    content = _extract_useful_content_from_response(response.json())
    core_logging.log_for_supervision(
        logger,
        logging.INFO,
        "Valid response from Ubble",
        extra={
            "status_code": response.status_code,
            "score": content.score,
            "status": content.status.value,  # type: ignore [union-attr]
            "document_type": content.document_type,
        }
        | base_extra_log,
    )
    return content


def download_ubble_picture(http_url: pydantic_networks.HttpUrl) -> tuple[str | None, typing.Any]:
    try:
        response = requests_utils.get(http_url, stream=True)
    except (urllib3_exceptions.HTTPError, requests_exceptions.RequestException) as e:
        raise requests_utils.ExternalAPIException(is_retryable=True) from e

    if response.status_code == 429 or response.status_code >= 500:
        logger.warning(
            "Ubble picture-download: external error",
            extra={"url": str(http_url), "status_code": response.status_code},
        )
        raise requests_utils.ExternalAPIException(is_retryable=True)

    if response.status_code == 403:
        logger.error(
            "Ubble picture-download: request has expired",
            extra={"url": str(http_url), "status_code": response.status_code},
        )
        raise requests_utils.ExternalAPIException(is_retryable=False)

    if response.status_code != 200:
        logger.error(  # pylint: disable=logging-fstring-interpolation
            f"Ubble picture-download: unexpected error: {response.status_code}",
            extra={"url": str(http_url)},
        )
        raise requests_utils.ExternalAPIException(is_retryable=False)

    return response.headers.get("content-type"), response.raw
