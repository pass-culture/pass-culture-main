"""
Implementation of the Ubble API.

See the documentation at https://docs.ubble.ai/
"""

import functools
import logging
import typing
from contextlib import suppress

from pydantic.v1 import networks as pydantic_networks
from pydantic.v1 import parse_obj_as
from urllib3 import exceptions as urllib3_exceptions

from pcapi import settings
from pcapi.connectors.serialization import ubble_serializers
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle
from pcapi.utils import requests
from pcapi.utils.rate_limit import RateLimitedError as RedisRateLimitedError
from pcapi.utils.rate_limit import rate_limit


logger = logging.getLogger(__name__)


class UbbleHttpError(Exception):
    pass


class UbbleConflictError(UbbleHttpError):
    pass


class UbbleRateLimitedError(UbbleHttpError):
    pass


class UbbleAssetExpiredError(UbbleHttpError):
    pass


class UbbleServerError(UbbleHttpError):
    pass


def log_and_handle_ubble_response(
    request_type: str,
) -> typing.Callable[[typing.Callable], typing.Callable]:
    def log_response_status_and_reraise_if_needed(ubble_function: typing.Callable) -> typing.Callable:
        @functools.wraps(ubble_function)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> ubble_schemas.UbbleContent:
            try:
                return ubble_function(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                response = e.response
                logger.error(
                    f"Ubble %s error: {response.status_code}",
                    request_type,
                    extra={
                        "alert": "Ubble error",
                        "error_type": "http",
                        "status_code": response.status_code,
                        "request_type": request_type,
                        "response_text": response.text,
                        "url": response.url,
                    },
                )
                if response.status_code == 409:
                    raise UbbleConflictError("Conflicting request was sent") from e

                if response.status_code == 429:
                    raise UbbleRateLimitedError("Ubble rate limit was reached") from e

                if response.status_code >= 500:
                    raise UbbleServerError("Ubble has server issues") from e

                raise UbbleHttpError(f"Unexpected Ubble error code {response.status_code}") from e

            except requests.exceptions.RequestException as e:
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
                raise UbbleServerError("Could not reach Ubble server") from e

        return wrapper

    return log_response_status_and_reraise_if_needed


def ubble_rate_limit[**P, T](func: typing.Callable[P, T]) -> typing.Callable[P, T]:
    def wrapper(*args: P.args, **kwds: P.kwargs) -> T:
        if not FeatureToggle.WIP_ASYNCHRONOUS_CELERY_UBBLE.is_active():
            return func(*args, **kwds)

        try:
            with rate_limit(
                key="connectors:ubble",
                time_window_size=settings.UBBLE_TIME_WINDOW_SIZE,
                max_per_time_window=settings.UBBLE_RATE_LIMIT,
            ):
                return func(*args, **kwds)
        except RedisRateLimitedError as e:
            raise UbbleRateLimitedError("Ubble rate limit was reached") from e

    return wrapper


@log_and_handle_ubble_response("applicant")
@ubble_rate_limit
def create_applicant(external_applicant_id: str, email: str) -> str:
    session = _configure_v2_session()
    response = session.post(
        build_url("/v2/applicants"),
        json={"external_applicant_id": external_applicant_id, "email": email},
        timeout=60,
    )
    response.raise_for_status()

    ubble_applicant = parse_obj_as(ubble_serializers.UbbleV2ApplicantResponse, response.json())

    logger.info(
        "Ubble applicant created",
        extra={
            "applicant_id": ubble_applicant.id,
            "external_applicant_id": ubble_applicant.external_applicant_id,
        },
    )

    return ubble_applicant.id


@log_and_handle_ubble_response("post-identity-verifications")
@ubble_rate_limit
def create_identity_verification(
    applicant_id: str, first_name: str, last_name: str, redirect_url: str, webhook_url: str
) -> ubble_schemas.UbbleContent:
    session = _configure_v2_session()
    response = session.post(
        build_url("/v2/identity-verifications"),
        json={
            "applicant_id": applicant_id,
            "declared_data": {"name": f"{first_name} {last_name}"},
            "redirect_url": redirect_url,
            "webhook_url": webhook_url,
        },
        timeout=60,
    )
    response.raise_for_status()

    ubble_identification = parse_obj_as(ubble_serializers.UbbleV2IdentificationResponse, response.json())
    ubble_content = ubble_serializers.convert_identification_to_ubble_content(ubble_identification)

    logger.info(
        "Ubble identification created",
        extra={"identification_id": ubble_identification.id, "status": str(ubble_identification.status)},
    )

    return ubble_content


@log_and_handle_ubble_response("identity-verifications-attempt")
@ubble_rate_limit
def create_identity_verification_attempt(identification_id: str, redirect_url: str) -> str:
    session = _configure_v2_session()
    response = session.post(
        build_url(f"/v2/identity-verifications/{identification_id}/attempts"),
        json={"redirect_url": redirect_url},
        timeout=60,
    )
    response.raise_for_status()

    identification_attempt = parse_obj_as(ubble_serializers.UbbleV2AttemptResponse, response.json())

    logger.info("Ubble identification attempted", extra={"identification_id": identification_attempt.id})

    return identification_attempt.links.verification_url.href


@log_and_handle_ubble_response("create-and-start-idv")
@ubble_rate_limit
def create_and_start_identity_verification(
    first_name: str, last_name: str, redirect_url: str, webhook_url: str
) -> ubble_schemas.UbbleContent:
    session = _configure_v2_session()
    response = session.post(
        build_url("/v2/create-and-start-idv"),
        json={
            "declared_data": {"name": f"{first_name} {last_name}"},
            "webhook_url": webhook_url,
            "redirect_url": redirect_url,
        },
        timeout=60,
    )
    response.raise_for_status()

    ubble_identification = parse_obj_as(ubble_serializers.UbbleV2IdentificationResponse, response.json())
    ubble_content = ubble_serializers.convert_identification_to_ubble_content(ubble_identification)

    logger.info(
        "Ubble identification created and started",
        extra={"identification_id": str(ubble_content.identification_id), "status": str(ubble_content.status)},
    )

    return ubble_content


@log_and_handle_ubble_response("get-identity-verifications")
@ubble_rate_limit
def get_identity_verification(identification_id: str) -> ubble_schemas.UbbleContent:
    response = requests.get(
        build_url(f"/v2/identity-verifications/{identification_id}"),
        cert=(settings.UBBLE_CLIENT_CERTIFICATE_PATH, settings.UBBLE_CLIENT_KEY_PATH),
        timeout=60,
    )
    response.raise_for_status()

    ubble_identification = parse_obj_as(ubble_serializers.UbbleV2IdentificationResponse, response.json())
    return ubble_serializers.convert_identification_to_ubble_content(ubble_identification)


@log_and_handle_ubble_response("get-attempts")
@ubble_rate_limit
def get_attempts(identification_id: str) -> list[ubble_serializers.AttemptData]:
    response = requests.get(
        build_url(f"/v2/identity-verifications/{identification_id}/attempts"),
        cert=(settings.UBBLE_CLIENT_CERTIFICATE_PATH, settings.UBBLE_CLIENT_KEY_PATH),
        timeout=60,
    )
    response.raise_for_status()

    deserialized_response = ubble_serializers.GetAttemptsResponse.model_validate(response.json())
    return deserialized_response.data


@log_and_handle_ubble_response("get-attempt-assets")
@ubble_rate_limit
def get_attempt_assets(identification_id: str, attempt_id: str) -> dict[ubble_serializers.AssetType, str]:
    response = requests.get(
        build_url(f"/v2/identity-verifications/{identification_id}/attempts/{attempt_id}/assets"),
        cert=(settings.UBBLE_CLIENT_CERTIFICATE_PATH, settings.UBBLE_CLIENT_KEY_PATH),
        timeout=60,
    )
    response.raise_for_status()

    deserialized_response = ubble_serializers.GetAttemptAssetsResponse.model_validate(response.json())
    return {asset.type: str(asset.links.asset_url.href) for asset in deserialized_response.data}


def request_webhook_notification(identification_id: str, webhook_url: str) -> None:
    """
    Request Ubble to call the webhook url with the given identification id data.
    This function is useful for development and post-outage recovery purposes.
    """
    session = _configure_v2_session()
    response = session.post(
        build_url(f"/v2/identity-verifications/{identification_id}/notify"),
        json={"webhook_url": webhook_url},
    )
    response.raise_for_status()


def _configure_v2_session() -> requests.Session:
    session = requests.Session()
    session.cert = (settings.UBBLE_CLIENT_CERTIFICATE_PATH, settings.UBBLE_CLIENT_KEY_PATH)
    return session


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
        if FeatureToggle.WIP_ASYNCHRONOUS_CELERY_UBBLE.is_active():
            raise UbbleAssetExpiredError("Asset has expired. It needs to be refetched before archiving.")
        raise requests.ExternalAPIException(is_retryable=False)

    if response.status_code != 200:
        logger.error(
            f"Ubble picture-download: unexpected error: {response.status_code}",
            extra={"url": str(http_url)},
        )
        raise requests.ExternalAPIException(is_retryable=False)

    return response.headers.get("content-type"), response.raw


# Ubble v1 (deprecated)

INCLUDED_MODELS = {
    "documents": ubble_serializers.UbbleIdentificationDocuments,
    "document-checks": ubble_serializers.UbbleIdentificationDocumentChecks,
    "reference-data-checks": ubble_serializers.UbbleIdentificationReferenceDataChecks,
}


def get_content(identification_id: str) -> ubble_schemas.UbbleContent:
    session = configure_session()
    base_extra_log = {"request_type": "get-content", "identification_id": identification_id}

    try:
        response = session.get(build_url(f"/identifications/{identification_id}/", identification_id), cert=None)
    except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
        logger.error(
            "Ubble get-content: Network error",
            extra=typing.cast(dict[str, typing.Any], {"exception": e, "error_type": "http"} | base_extra_log),
        )
        raise requests.ExternalAPIException(is_retryable=True) from e

    if not response.ok:
        if response.status_code >= 500 or response.status_code == 429:
            logger.error(
                "Ubble get-content: External error: %s",
                response.status_code,
                extra={"response_text": response.text, "error_type": "http", "status_code": response.status_code}
                | base_extra_log,
            )
            raise requests.ExternalAPIException(is_retryable=True)

        logger.error(
            # ungroup errors on sentry
            f"Ubble get-content: Unexpected error: {response.status_code}, {response.text}",
            extra=typing.cast(
                dict[str, typing.Any],
                {"response_text": response.text, "status_code": response.status_code, "error_type": "http"}
                | base_extra_log,
            ),
        )
        raise requests.ExternalAPIException(is_retryable=False)

    content = _extract_useful_content_from_response(response.json())
    logger.info(
        "Valid response from Ubble",
        extra=typing.cast(
            dict[str, typing.Any],
            {
                "status_code": response.status_code,
                "score": content.score,
                "status": content.status.value if content.status else None,
                "document_type": content.document_type,
            }
            | base_extra_log,
        ),
    )
    return content


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


def _get_included_attributes(response: dict, type_: str) -> ubble_serializers.UbbleIdentificationObject | None:
    filtered = [incl for incl in response["included"] if incl["type"] == type_]
    if not filtered:
        return None
    return INCLUDED_MODELS[type_](**filtered[0].get("attributes"))


def _get_data_attribute(response: dict, name: str) -> typing.Any:
    return response["data"]["attributes"].get(name)


def _get_data_relationships(response: dict, name: str) -> typing.Any:
    return response["data"]["relationships"].get(name)


def _parse_reason_codes(response: dict) -> list[subscription_models.FraudReasonCode]:
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
    default = subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER
    reason_codes_data = _get_data_relationships(response, "reason-codes")
    reason_codes_numbers = [int(item["id"]) for item in reason_codes_data["data"] if item["type"] == "reason-codes"]
    reason_codes = [ubble_schemas.UBBLE_REASON_CODE_MAPPING.get(number, default) for number in reason_codes_numbers]
    return reason_codes


def _parse_ubble_gender(ubble_gender: str | None) -> users_models.GenderEnum | None:
    if not ubble_gender:
        return None
    with suppress(KeyError):
        return users_models.GenderEnum[ubble_gender]
    return None


def _extract_useful_content_from_response(response: dict) -> ubble_schemas.UbbleContent:
    documents = typing.cast(
        ubble_serializers.UbbleIdentificationDocuments, _get_included_attributes(response, "documents")
    )
    document_checks = typing.cast(
        ubble_serializers.UbbleIdentificationDocumentChecks, _get_included_attributes(response, "document-checks")
    )
    reference_data_checks = typing.cast(
        ubble_serializers.UbbleIdentificationReferenceDataChecks,
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

    content = ubble_schemas.UbbleContent(
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
