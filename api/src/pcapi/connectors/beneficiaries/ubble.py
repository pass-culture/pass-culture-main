import logging
import typing
import urllib.parse

import requests

from pcapi import settings
from pcapi.connectors.beneficiaries import exceptions
from pcapi.core import logging as core_logging
from pcapi.core.fraud.ubble import models as ubble_fraud_models


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
        reference_data_check_score=getattr(reference_data_checks, "score", None),
        registration_datetime=registered_at,
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
    except IOError as e:
        # Any exception explicitely raised by requests or urllib3 inherits from IOError
        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            "Request error while starting Ubble identification: %s",
            e,
            extra={
                "alert": "Ubble error",
                "error_type": "network",
                "request_type": "start-identification",
            },
        )
        raise exceptions.IdentificationServiceUnavailable()

    if not response.ok:
        # https://ubbleai.github.io/developer-documentation/#errors
        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            "Error while starting Ubble identification: %s, %s",
            response.status_code,
            response.text,
            extra={
                "alert": "Ubble error",
                "error_type": "http",
                "status_code": response.status_code,
                "request_type": "start-identification",
            },
        )
        if response.status_code in (410, 429):
            raise exceptions.IdentificationServiceUnavailable()
        # Other errors should not happen, so keep them different than Ubble unavailable
        raise exceptions.IdentificationServiceError()

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
    response = session.get(build_url(f"/identifications/{identification_id}/"))

    if not response.ok:
        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            "Error while fetching Ubble identification",
            extra={
                "status_code": response.status_code,
                "identification_id": identification_id,
                "request_type": "get-content",
                "error_type": "http",
            },
        )
        response.raise_for_status()

    content = _extract_useful_content_from_response(response.json())
    core_logging.log_for_supervision(
        logger,
        logging.INFO,
        "Valid response from Ubble",
        extra={
            "status_code": response.status_code,
            "identification_id": identification_id,
            "score": content.score,
            "status": content.status.value,  # type: ignore [union-attr]
            "request_type": "get-content",
            "document_type": content.document_type,
        },
    )
    return content
