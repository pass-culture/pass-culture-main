import enum
from typing import Any

import pcapi.core.external_bookings.cds.exceptions as cds_exceptions
from pcapi.utils import requests


class ResourceCDS(enum.Enum):
    TARIFFS = "tariffs"
    RATING = "rating"


def _extract_reason_from_response(response: requests.Response) -> str:
    # from requests.Response.raise_for_status()
    if isinstance(response.reason, bytes):
        try:
            reason = response.reason.decode("utf-8")
        except UnicodeDecodeError:
            reason = response.reason.decode("iso-8859-1")
    else:
        reason = response.reason
    return reason


def _check_response_is_ok(response: requests.Response, cinema_api_token: str | None, request_detail: str) -> None:
    if response.status_code >= 400:
        reason = _extract_reason_from_response(response)
        error_message = _filter_token(reason, cinema_api_token)
        raise cds_exceptions.CineDigitalServiceAPIException(f"Error on CDS API on {request_detail} : {error_message}")


def get_resource(
    api_url: str,
    account_id: str,
    cinema_api_token: str | None,
    resource: ResourceCDS,
    path_params: dict[str, Any] | None = None,
    *,
    request_timeout: int | None = None,
) -> dict | list[dict] | list:
    url = _build_url(api_url, account_id, cinema_api_token, resource, path_params)
    response = requests.get(url, timeout=request_timeout)

    _check_response_is_ok(response, cinema_api_token, f"GET {resource}")

    return response.json()


def _build_url(
    api_url: str,
    account_id: str,
    cinema_api_token: str | None,
    resource: ResourceCDS,
    path_params: dict[str, Any] | None = None,
) -> str:
    resource_url = resource.value
    if path_params:
        for key, value in path_params.items():
            resource_url = resource_url.replace(":" + key, str(value))
    return f"https://{account_id}.{api_url}{resource_url}?api_token={cinema_api_token}"


def _filter_token(error_message: str, token: str | None) -> str:
    if isinstance(token, str) and token in error_message:
        error_message = error_message.replace(token, "")
    return error_message
