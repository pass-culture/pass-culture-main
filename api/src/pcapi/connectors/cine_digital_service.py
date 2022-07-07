import enum
from typing import Any
from typing import Optional

from pcapi import settings
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedCancelBookingSuccess
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedMovies
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedPaymentType
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedScreens
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedSeatMap
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedShows
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedTariffs
from pcapi.routes.serialization import BaseModel
from pcapi.utils import requests


class ResourceCDS(enum.Enum):
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
    ResourceCDS.SHOWS: MockedShows,
    ResourceCDS.PAYMENT_TYPE: MockedPaymentType,
    ResourceCDS.TARIFFS: MockedTariffs,
    ResourceCDS.SCREENS: MockedScreens,
    ResourceCDS.CANCEL_BOOKING: MockedCancelBookingSuccess,
    ResourceCDS.SEATMAP: MockedSeatMap,
    ResourceCDS.MEDIA: MockedMovies,
}


def get_resource(
    api_url: str,
    cinema_id: str,
    cinema_api_token: Optional[str],
    resource: ResourceCDS,
    path_params: Optional[dict[str, Any]] = None,
) -> dict | list[dict] | list:

    if settings.IS_DEV:
        return MOCKS[resource]

    try:
        url = _build_url(api_url, cinema_id, cinema_api_token, resource, path_params)
        response = requests.get(url)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        error_message = _filter_token(str(e), cinema_api_token)
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error on CDS API on GET {resource} : {error_message}"
        ) from None

    return response.json()


def put_resource(
    api_url: str, cinema_id: str, cinema_api_token: Optional[str], resource: ResourceCDS, body: BaseModel
) -> Optional[dict | list[dict] | list]:
    if settings.IS_DEV:
        return MOCKS[resource]

    try:
        url = _build_url(api_url, cinema_id, cinema_api_token, resource)
        headers = {"Content-Type": "application/json"}
        response = requests.put(url, headers=headers, data=body.json(by_alias=True))
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        error_message = _filter_token(str(e), cinema_api_token)
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error on CDS API on PUT {resource} : {error_message}"
        ) from None

    response_headers = response.headers.get("Content-Type")
    if response_headers and "application/json" in response_headers:
        return response.json()
    return None


def post_resource(
    api_url: str, cinema_id: str, cinema_api_token: Optional[str], resource: ResourceCDS, body: BaseModel
) -> dict:
    try:
        url = _build_url(api_url, cinema_id, cinema_api_token, resource)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=body.json(by_alias=True))
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        error_message = _filter_token(str(e), cinema_api_token)
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error on CDS API on POST {resource} : {error_message}"
        ) from None

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
    cinema_id: str,
    cinema_api_token: Optional[str],
    resource: ResourceCDS,
    path_params: Optional[dict[str, Any]] = None,
) -> str:
    resource_url = resource.value
    if path_params:
        for key, value in path_params.items():
            resource_url = resource_url.replace(":" + key, str(value))
    return f"https://{cinema_id}.{api_url}{resource_url}?api_token={cinema_api_token}"


def _filter_token(error_message: str, token: Optional[str]) -> str:
    if isinstance(token, str) and token in error_message:
        error_message = error_message.replace(token, "")
    return error_message
