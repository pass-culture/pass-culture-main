import enum
from typing import Any
from typing import Optional
from typing import Union

from pcapi import settings
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedCancelBookingSuccess
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
    PAYMENT_TYPE = "paiementtype"
    SCREENS = "screens"
    SEATMAP = "shows/:show_id/seatmap"
    CANCEL_BOOKING = "transaction/cancel"


MOCKS: dict[ResourceCDS, Union[dict, list[dict], list]] = {
    ResourceCDS.SHOWS: MockedShows,
    ResourceCDS.PAYMENT_TYPE: MockedPaymentType,
    ResourceCDS.TARIFFS: MockedTariffs,
    ResourceCDS.SCREENS: MockedScreens,
    ResourceCDS.CANCEL_BOOKING: MockedCancelBookingSuccess,
    ResourceCDS.SEATMAP: MockedSeatMap,
}


def get_resource(
    api_url: str,
    cinema_id: str,
    token: Optional[str],
    resource: ResourceCDS,
    path_params: Optional[dict[str, Any]] = None,
) -> Union[dict, list[dict], list]:

    if settings.IS_DEV:
        return MOCKS[resource]

    try:
        url = _build_url(api_url, cinema_id, token, resource, path_params)
        response = requests.get(url)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise cds_exceptions.CineDigitalServiceAPIException(f"API CDS - url : {url} - error : {e}")

    return response.json()


def put_resource(
    api_url: str, cinema_id: str, token: Optional[str], resource: ResourceCDS, body: BaseModel
) -> Optional[Union[dict, list[dict], list]]:
    if settings.IS_DEV:
        return MOCKS[resource]

    try:
        url = _build_url(api_url, cinema_id, token, resource)
        headers = {"Content-Type": "application/json"}
        response = requests.put(url, headers=headers, data=body.json(by_alias=True))
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise cds_exceptions.CineDigitalServiceAPIException(f"API CDS - url : {url} - error : {e}")

    response_headers = response.headers.get("Content-Type")
    if response_headers and "application/json" in response_headers:
        return response.json()
    return None


def _build_url(
    api_url: str,
    cinema_id: str,
    token: Optional[str],
    resource: ResourceCDS,
    path_params: Optional[dict[str, Any]] = None,
) -> str:
    resource_url = resource.value
    if path_params:
        for key, value in path_params.items():
            resource_url = resource_url.replace(":" + key, str(value))
    return f"https://{cinema_id}.{api_url}{resource_url}?api_token={token}"
