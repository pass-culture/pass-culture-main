from contextlib import suppress
import functools
import logging
import typing

from pydantic.v1 import networks as pydantic_networks
from pydantic.v1 import parse_obj_as
from urllib3 import exceptions as urllib3_exceptions

from pcapi import settings
from pcapi.connectors.serialization import ubble_serializers
from pcapi.core import logging as core_logging
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle
from pcapi.utils import requests


logger = logging.getLogger(__name__)


INCLUDED_MODELS = {
    "documents": ubble_fraud_models.UbbleIdentificationDocuments,
    "document-checks": ubble_fraud_models.UbbleIdentificationDocumentChecks,
    "reference-data-checks": ubble_fraud_models.UbbleIdentificationReferenceDataChecks,
}


def start_identification(
    user_id: int, first_name: str, last_name: str, webhook_url: str, redirect_url: str
) -> fraud_models.UbbleContent:
    ubble_backend = _get_ubble_backend()
    return ubble_backend.start_identification(user_id, first_name, last_name, webhook_url, redirect_url)


def get_content(identification_id: str) -> fraud_models.UbbleContent:
    ubble_backend = _get_ubble_backend()
    return ubble_backend.get_content(identification_id)


def download_ubble_picture(http_url: pydantic_networks.HttpUrl) -> tuple[str | None, typing.Any]:
    try:
        response = requests.get(http_url, stream=True)
    except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
        raise requests.ExternalAPIException(is_retryable=True) from e

    if response.status_code == 429 or response.status_code >= 500:
        logger.warning(
            "Ubble picture-download: external error",
            extra={"url": str(http_url), "status_code": response.status_code},
        )
        raise requests.ExternalAPIException(is_retryable=True)

    if response.status_code == 403:
        logger.error(
            "Ubble picture-download: request has expired",
            extra={"url": str(http_url), "status_code": response.status_code},
        )
        raise requests.ExternalAPIException(is_retryable=False)

    if response.status_code != 200:
        logger.error(  # pylint: disable=logging-fstring-interpolation
            f"Ubble picture-download: unexpected error: {response.status_code}",
            extra={"url": str(http_url)},
        )
        raise requests.ExternalAPIException(is_retryable=False)

    return response.headers.get("content-type"), response.raw


class UbbleBackend:
    def start_identification(  # pylint: disable=too-many-positional-arguments
        self,
        user_id: int,
        first_name: str,
        last_name: str,
        webhook_url: str,
        redirect_url: str,
    ) -> fraud_models.UbbleContent:
        raise NotImplementedError()

    def get_content(self, identification_id: str) -> fraud_models.UbbleContent:
        raise NotImplementedError()


P = typing.ParamSpec("P")


def log_and_handle_response_status(
    request_type: str,
) -> typing.Callable[[typing.Callable[P, fraud_models.UbbleContent]], typing.Callable[P, fraud_models.UbbleContent]]:
    def log_response_status_and_reraise_if_needed(
        ubble_content_function: typing.Callable[P, fraud_models.UbbleContent]
    ) -> typing.Callable[P, fraud_models.UbbleContent]:
        @functools.wraps(ubble_content_function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> fraud_models.UbbleContent:
            try:
                ubble_content = ubble_content_function(*args, **kwargs)

                logger.info(
                    "Valid response from Ubble",
                    extra={"identification_id": str(ubble_content.identification_id), "request_type": request_type},
                )

                return ubble_content
            except requests.exceptions.HTTPError as e:
                response = e.response
                if response.status_code == 429 or response.status_code >= 500:
                    logger.error(
                        f"Ubble {request_type}: External error: %s",
                        response.status_code,
                        extra={
                            "alert": "Ubble error",
                            "error_type": "http",
                            "status_code": response.status_code,
                            "request_type": request_type,
                            "response_text": response.text,
                            "url": response.url,
                        },
                    )
                    raise requests.ExternalAPIException(is_retryable=True) from e

                logger.error(
                    f"Ubble {request_type}: Unexpected error: %s",
                    response.status_code,
                    extra={
                        "alert": "Ubble error",
                        "error_type": "http",
                        "status_code": response.status_code,
                        "request_type": request_type,
                        "response_text": response.text,
                        "url": response.url,
                    },
                )
                raise requests.ExternalAPIException(is_retryable=True) from e
            except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
                logger.error(
                    "Ubble %s: Network error",
                    request_type,
                    extra={
                        "exception": e,
                        "alert": "Ubble error",
                        "error_type": "network",
                        "request_type": request_type,
                    },
                )
                raise requests.ExternalAPIException(is_retryable=True) from e

        return wrapper

    return log_response_status_and_reraise_if_needed


class UbbleV2Backend(UbbleBackend):
    @log_and_handle_response_status("create-and-start-idv")
    def start_identification(  # pylint: disable=too-many-positional-arguments
        self,
        user_id: int,
        first_name: str,
        last_name: str,
        webhook_url: str,
        redirect_url: str,
    ) -> fraud_models.UbbleContent:
        response = requests.post(
            build_url("/v2/create-and-start-idv", user_id),
            json={
                "declared_data": {"name": f"{first_name} {last_name}"},
                "webhook_url": webhook_url,
                "redirect_url": redirect_url,
            },
            cert=(settings.UBBLE_CLIENT_CERTIFICATE_PATH, settings.UBBLE_CLIENT_KEY_PATH),
        )
        response.raise_for_status()

        ubble_identification = parse_obj_as(ubble_serializers.UbbleIdentificationResponse, response.json())
        ubble_content = ubble_serializers.convert_identification_to_ubble_content(ubble_identification)

        logger.info(
            "Ubble identification started",
            extra={"identification_id": str(ubble_content.identification_id), "status": str(ubble_content.status)},
        )

        return ubble_content

    def get_content(self, identification_id: str) -> fraud_models.UbbleContent:
        raise NotImplementedError()


class UbbleV1Backend(UbbleBackend):
    def start_identification(  # pylint: disable=too-many-positional-arguments
        self,
        user_id: int,
        first_name: str,
        last_name: str,
        webhook_url: str,
        redirect_url: str,
    ) -> fraud_models.UbbleContent:
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
            response = session.post(build_url("/identifications/", user_id), json=data)
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
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
            raise requests.ExternalAPIException(is_retryable=True) from e

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
                raise requests.ExternalAPIException(is_retryable=True)

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

            raise requests.ExternalAPIException(is_retryable=False)

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

    def get_content(self, identification_id: str) -> fraud_models.UbbleContent:
        session = configure_session()
        base_extra_log = {"request_type": "get-content", "identification_id": identification_id}

        try:
            response = session.get(build_url(f"/identifications/{identification_id}/", identification_id))
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
            core_logging.log_for_supervision(
                logger,
                logging.ERROR,
                "Ubble get-content: Network error",
                extra={"exception": e, "error_type": "http"} | base_extra_log,
            )
            raise requests.ExternalAPIException(is_retryable=True) from e

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
                raise requests.ExternalAPIException(is_retryable=True)

            core_logging.log_for_supervision(
                logger,
                logging.ERROR,
                f"Ubble get-content: Unexpected error: {response.status_code}, {response.text}",  # ungroup errors on sentry
                extra={"response_text": response.text, "status_code": response.status_code, "error_type": "http"}
                | base_extra_log,
            )
            raise requests.ExternalAPIException(is_retryable=False)

        content = _extract_useful_content_from_response(response.json())
        core_logging.log_for_supervision(
            logger,
            logging.INFO,
            "Valid response from Ubble",
            extra={
                "status_code": response.status_code,
                "score": content.score,
                "status": content.status.value if content.status else None,
                "document_type": content.document_type,
            }
            | base_extra_log,
        )
        return content


def _get_ubble_backend() -> UbbleBackend:
    if FeatureToggle.WIP_UBBLE_V2.is_active():
        return UbbleV2Backend()
    return UbbleV1Backend()


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


def _should_use_mock(id_: int | str | None = None) -> bool:
    if not settings.UBBLE_MOCK_API_URL or not id_:
        return False

    response = requests.get(f"{settings.UBBLE_MOCK_API_URL}/id_exists/{id_}")
    return response.status_code == 200


def build_url(path: str, id_: int | str | None = None) -> str:
    base_url = settings.UBBLE_API_URL
    if settings.UBBLE_MOCK_API_URL and _should_use_mock(id_):
        base_url = settings.UBBLE_MOCK_API_URL

    base_url = base_url.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path

    return base_url + path


def _get_included_attributes(response: dict, type_: str) -> ubble_fraud_models.UbbleIdentificationObject | None:
    filtered = [incl for incl in response["included"] if incl["type"] == type_]
    if not filtered:
        return None
    return INCLUDED_MODELS[type_](**filtered[0].get("attributes"))


def _get_data_attribute(response: dict, name: str) -> typing.Any:
    return response["data"]["attributes"].get(name)


def _get_data_relationships(response: dict, name: str) -> typing.Any:
    return response["data"]["relationships"].get(name)


def _parse_reason_codes(response: dict) -> list[fraud_models.FraudReasonCode]:
    """
    Format to parse
    reason-codes: {
        "meta": {"count": 2},
        "data": [
            {"type": "reason-codes", "id": 1304},
            {"type": "reason-codes", "id": 1310}
        ]
    }
    """
    default = fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER
    reason_codes_data = _get_data_relationships(response, "reason-codes")
    reason_codes_numbers = [int(item["id"]) for item in reason_codes_data["data"] if item["type"] == "reason-codes"]
    reason_codes = [fraud_models.UBBLE_REASON_CODE_MAPPING.get(number, default) for number in reason_codes_numbers]
    return reason_codes


def _parse_ubble_gender(ubble_gender: str | None) -> users_models.GenderEnum | None:
    if not ubble_gender:
        return None
    with suppress(KeyError):
        return users_models.GenderEnum[ubble_gender]
    return None


def _extract_useful_content_from_response(
    response: dict,
) -> fraud_models.UbbleContent:
    documents = typing.cast(
        ubble_fraud_models.UbbleIdentificationDocuments, _get_included_attributes(response, "documents")
    )
    document_checks = typing.cast(
        ubble_fraud_models.UbbleIdentificationDocumentChecks, _get_included_attributes(response, "document-checks")
    )
    reference_data_checks = typing.cast(
        ubble_fraud_models.UbbleIdentificationReferenceDataChecks,
        _get_included_attributes(response, "reference-data-checks"),
    )

    comment = _get_data_attribute(response, "comment")
    identification_id = _get_data_attribute(response, "identification-id")
    identification_url = _get_data_attribute(response, "identification-url")
    registered_at = _get_data_attribute(response, "created-at")
    processed_at = _get_data_attribute(response, "ended-at")
    score = _get_data_attribute(response, "score")
    status = _get_data_attribute(response, "status")
    status_updated_at = _get_data_attribute(response, "status-updated-at")

    content = fraud_models.UbbleContent(
        birth_date=getattr(documents, "birth_date", None),
        comment=comment,
        document_type=getattr(documents, "document_type", None),
        expiry_date_score=getattr(document_checks, "expiry_date_score", None),
        first_name=getattr(documents, "first_name", None),
        id_document_number=getattr(documents, "document_number", None),
        identification_id=identification_id,
        identification_url=identification_url,
        gender=_parse_ubble_gender(getattr(documents, "gender", None)),
        last_name=getattr(documents, "last_name", None),
        married_name=getattr(documents, "married_name", None),
        ove_score=getattr(document_checks, "ove_score", None),
        reason_codes=_parse_reason_codes(response),
        reference_data_check_score=getattr(reference_data_checks, "score", None),
        registration_datetime=registered_at,
        processed_datetime=processed_at,
        score=score,
        status=status,
        status_updated_at=status_updated_at,
        supported=getattr(document_checks, "supported", None),
        signed_image_front_url=getattr(documents, "signed_image_front_url", None),
        signed_image_back_url=getattr(documents, "signed_image_back_url", None),
    )
    return content
