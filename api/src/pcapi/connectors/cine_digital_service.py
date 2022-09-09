import enum
from typing import Any

from pcapi import settings
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedCancelBookingSuccess
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedCinemas
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedMovies
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedPaymentType
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedScreens
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedSeatMap
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedShows
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedTariffs
from pcapi.routes.serialization import BaseModel
from pcapi.utils import requests


class ResourceCDS(enum.Enum):
    CINEMAS = "cinemas"
    TARIFFS = "tariffs"
    SHOWS = "shows"
    MEDIA = "media"
    PAYMENT_TYPE = "paiementtype"
    VOUCHER_TYPE = "vouchertype"
    SCREENS = "screens"
    SEATMAP = "shows/:show_id/seatmap"
    CREATE_TRANSACTION = "transaction/create"
    CANCEL_BOOKING = "transaction/cancel"


MOCKS: dict[ResourceCDS, dict | list[dict] | list] = {
    ResourceCDS.CINEMAS: MockedCinemas,
    ResourceCDS.SHOWS: MockedShows,
    ResourceCDS.PAYMENT_TYPE: MockedPaymentType,
    ResourceCDS.TARIFFS: MockedTariffs,
    ResourceCDS.SCREENS: MockedScreens,
    ResourceCDS.CANCEL_BOOKING: MockedCancelBookingSuccess,
    ResourceCDS.SEATMAP: MockedSeatMap,
    ResourceCDS.MEDIA: MockedMovies,
}


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
) -> dict | list[dict] | list:

    if settings.IS_DEV:
        return MOCKS[resource]

    url = _build_url(api_url, account_id, cinema_api_token, resource, path_params)
    response = requests.get(url)

    _check_response_is_ok(response, cinema_api_token, f"GET {resource}")

    return response.json()


def put_resource(
    api_url: str, account_id: str, cinema_api_token: str | None, resource: ResourceCDS, body: BaseModel
) -> dict | list[dict] | list | None:
    if settings.IS_DEV:
        return MOCKS[resource]

    url = _build_url(api_url, account_id, cinema_api_token, resource)
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, headers=headers, data=body.json(by_alias=True))

    _check_response_is_ok(response, cinema_api_token, f"PUT {resource}")

    response_headers = response.headers.get("Content-Type")
    if response_headers and "application/json" in response_headers:
        return response.json()
    return None


def post_resource(
    api_url: str, account_id: str, cinema_api_token: str | None, resource: ResourceCDS, body: BaseModel
) -> dict:
    url = _build_url(api_url, account_id, cinema_api_token, resource)
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=body.json(by_alias=True))

    _check_response_is_ok(response, cinema_api_token, f"POST {resource}")

    return response.json()


def get_movie_poster_from_api(image_url: str) -> bytes:
    api_response = requests.get(image_url)

    if api_response.status_code != 200:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error getting CDS API movie poster {image_url}" f" with code {api_response.status_code}"
        )

    return api_response.content


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
