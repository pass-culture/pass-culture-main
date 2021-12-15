import datetime
import logging
import typing
import urllib.parse

import requests

from pcapi import settings
from pcapi.connectors.beneficiaries import exceptions
from pcapi.core import logging as core_logging
from pcapi.core.fraud.models import ubble as ubble_models


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
    "documents": ubble_models.UbbleIdentificationDocuments,
    "document-checks": ubble_models.UbbleIdentificationDocumentChecks,
    "face-checks": ubble_models.UbbleIdentificationFaceChecks,
    "reference-data-checks": ubble_models.UbbleIdentificationReferenceDataChecks,
    "doc-face-matches": ubble_models.UbbleIdentificationDocFaceMatches,
}


def _get_included_attributes(
    response: ubble_models.UbbleIdentificationResponse, type_: str
) -> typing.Union[ubble_models.UbbleIdentificationDocuments, ubble_models.UbbleIdentificationDocumentChecks,]:
    filtered = list(filter(lambda included: included["type"] == type_, response["included"]))
    attributes = INCLUDED_MODELS[type_](**filtered[0].get("attributes")) if filtered else None
    return attributes


def _get_data_attribute(response: ubble_models.UbbleIdentificationResponse, name: str) -> typing.Any:
    return response["data"]["attributes"].get(name)


def _extract_useful_content_from_response(
    response: ubble_models.UbbleIdentificationResponse,
) -> ubble_models.UbbleContent:
    documents: ubble_models.UbbleIdentificationDocuments = _get_included_attributes(response, "documents")
    document_checks: ubble_models.UbbleIdentificationDocumentChecks = _get_included_attributes(
        response, "document-checks"
    )
    score = _get_data_attribute(response, "score")
    comment = _get_data_attribute(response, "comment")
    identification_id = _get_data_attribute(response, "identification-id")
    identification_url = _get_data_attribute(response, "identification-url")
    status = _get_data_attribute(response, "status")
    registered_at = _get_data_attribute(response, "created-at")

    content = ubble_models.UbbleContent(
        status=status,
        birth_date=getattr(documents, "birth_date", None),
        first_name=getattr(documents, "first_name", None),
        last_name=getattr(documents, "last_name", None),
        document_type=getattr(documents, "document_type", None),
        id_document_number=getattr(documents, "document_number", None),
        score=score,
        comment=comment,
        expiry_date_score=getattr(document_checks, "expiry_date_score", None),
        supported=getattr(document_checks, "supported", None),
        identification_id=identification_id,
        identification_url=identification_url,
        registration_datetime=registered_at,
    )
    return content


def start_identification(
    user_id: int,
    phone_number: str,
    birth_date: datetime.date,
    first_name: str,
    last_name: str,
    webhook_url: str,
    redirect_url: str,
) -> ubble_models.UbbleContent:
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
    return content


def get_content(identification_id: str, override_scores: bool = False) -> ubble_models.UbbleContent:
    session = configure_session()
    response = session.get(
        build_url(f"/identifications/{identification_id}/"),
    )

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

    response_body = response.json()
    if override_scores:
        _override_scores(response_body)
    content = _extract_useful_content_from_response(response_body)

    core_logging.log_for_supervision(
        logger,
        logging.INFO,
        "Valid response from Ubble",
        extra={
            "status_code": response.status_code,
            "identification_id": identification_id,
            "score": content.score,
            "status": content.status.value,
            "request_type": "get-content",
        },
    )
    return content


def _override_scores(response: ubble_models.UbbleIdentificationResponse) -> None:
    response["data"]["attributes"]["score"] = ubble_models.UbbleScore.VALID.value

    doc_face_matches = next(filter(lambda i: i["type"] == "doc-face-matches", response["included"]))
    doc_face_matches["attributes"]["score"] = ubble_models.UbbleScore.VALID.value

    document_checks = next(filter(lambda i: i["type"] == "document-checks", response["included"]))
    document_checks["attributes"]["data-extracted-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["expiry-date-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["issue-date-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["live-video-capture-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["mrz-validity-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["mrz-viz-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["ove-back-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["ove-front-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["ove-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["quality-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["supported"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["visual-back-score"] = ubble_models.UbbleScore.VALID.value
    document_checks["attributes"]["visual-front-score"] = ubble_models.UbbleScore.VALID.value

    face_chekcs = next(filter(lambda i: i["type"] == "face-checks", response["included"]))
    face_chekcs["attributes"]["active-liveness-score"] = ubble_models.UbbleScore.VALID.value
    face_chekcs["attributes"]["live-video-capture-score"] = ubble_models.UbbleScore.VALID.value
    face_chekcs["attributes"]["quality-score"] = ubble_models.UbbleScore.VALID.value
    face_chekcs["attributes"]["score"] = ubble_models.UbbleScore.VALID.value

    reference_data_checks = next(filter(lambda i: i["type"] == "reference-data-checks", response["included"]))
    reference_data_checks["attributes"]["score"] = ubble_models.UbbleScore.VALID.value
