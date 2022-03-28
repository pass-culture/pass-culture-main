from pydantic import parse_obj_as

from pcapi import settings
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions
from pcapi.core.booking_providers.cds.mocked_api_calls import MockedShows
from pcapi.utils import requests


def get_shows(cinema_id: str, url: str, token: str) -> list[ShowCDS]:

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
    shows = parse_obj_as(list[ShowCDS], json_response)

    return shows
