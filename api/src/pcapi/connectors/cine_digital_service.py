from pydantic import parse_obj_as

from pcapi import settings
import pcapi.connectors.serialization.cine_digital_service_serializers as cds_serializers
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedPaymentType
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedScreens
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedShows
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedTariffs
from pcapi.utils import requests


def get_shows(cinema_id: str, url: str, token: str) -> list[cds_serializers.ShowCDS]:

    api_url = f"https://{cinema_id}.{url}shows?api_token={token}"

    try:
        if not settings.IS_DEV:
            api_response = requests.get(api_url)
        else:
            api_response = MockedShows()
    except Exception:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error connecting CDS for cinemaId={cinema_id} & url={url}"
        )

    if api_response.status_code != 200:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error getting Cine Digital Service API DATA for cinemaId={cinema_id} & url={url}"
        )

    json_response = api_response.json()
    shows = parse_obj_as(list[cds_serializers.ShowCDS], json_response)

    return shows


def get_payment_types(cinema_id: str, url: str, token: str) -> cds_serializers.PaymentTypeCDS:

    api_url = f"https://{cinema_id}.{url}paiementtype?api_token={token}"
    try:
        if not settings.IS_DEV:
            api_response = requests.get(api_url)
        else:
            api_response = MockedPaymentType()
    except Exception:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error connecting CDS for cinemaId={cinema_id} & url={url}"
        )

    if api_response.status_code != 200:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error getting Cine Digital Service API DATA for cinemaId={cinema_id} & url={url}"
        )

    json_response = api_response.json()
    payment_types = parse_obj_as(list[cds_serializers.PaymentTypeCDS], json_response)

    return payment_types


def get_tariffs(cinema_id: str, url: str, token: str) -> list[cds_serializers.TariffCDS]:

    api_url = f"https://{cinema_id}.{url}tariffs?api_token={token}"

    try:
        if not settings.IS_DEV:
            api_response = requests.get(api_url)
        else:
            api_response = MockedTariffs()
    except Exception:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error connecting CDS for cinemaId={cinema_id} & url={url}"
        )

    if api_response.status_code != 200:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error getting Cine Digital Service API DATA for cinemaId={cinema_id} & url={url}"
        )

    json_response = api_response.json()
    tariffs = parse_obj_as(list[cds_serializers.TariffCDS], json_response)

    return tariffs


def get_screens(cinema_id: str, url: str, token: str) -> list[cds_serializers.ShowCDS]:

    api_url = f"https://{cinema_id}.{url}screens?api_token={token}"

    try:
        if not settings.IS_DEV:
            api_response = requests.get(api_url)
        else:
            api_response = MockedScreens()
    except Exception:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error connecting CDS for cinemaId={cinema_id} & url={url}"
        )

    if api_response.status_code != 200:
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Error getting Cine Digital Service API DATA for cinemaId={cinema_id} & url={url}"
        )

    json_response = api_response.json()
    screens = parse_obj_as(list[cds_serializers.ScreenCDS], json_response)

    return screens
