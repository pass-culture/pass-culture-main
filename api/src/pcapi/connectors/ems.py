import json

from pydantic import parse_obj_as
from requests.auth import HTTPBasicAuth

from pcapi import settings
from pcapi.connectors.serialization import ems_serializers
from pcapi.connectors.serialization.ems_serializers import CinemasProgramsResponse
from pcapi.core.external_bookings.ems.exceptions import EMSAPIException
from pcapi.utils import requests


def _build_url() -> str:
    return settings.EMS_API_URL


def _build_query_params(version: int) -> dict:
    return {"version": version}


def _build_auth() -> HTTPBasicAuth:
    auth = HTTPBasicAuth(username=settings.EMS_API_USER, password=settings.EMS_API_PASSWORD)
    return auth


def get_cinemas_programs(version: int = 0) -> CinemasProgramsResponse:
    response = requests.get(url=_build_url(), auth=_build_auth(), params=_build_query_params(version))

    _check_response_is_ok(response)
    return parse_obj_as(ems_serializers.CinemasProgramsResponse, response.json())


def get_movie_poster_from_api(image_url: str) -> bytes:
    api_response = requests.get(image_url)

    if api_response.status_code != 200:
        raise EMSAPIException(f"Error getting EMS API movie poster {image_url} with code {api_response.status_code}")

    return api_response.content


def _check_response_is_ok(response: requests.Response) -> None:
    if response.status_code >= 400:
        reason = _extract_reason_from_response(response)
        message = _extract_message_from_response(response)
        error_message = _filter_credentials(reason)
        raise EMSAPIException(f"Error on EMS API call {error_message} - {message}")


def _extract_reason_from_response(response: requests.Response) -> str:
    if isinstance(response.reason, bytes):
        try:
            reason = response.reason.decode("utf-8")
        except UnicodeDecodeError:
            reason = response.reason.decode("iso-8859-1")
    else:
        reason = response.reason
    return reason


def _extract_message_from_response(response: requests.Response) -> str:
    try:
        content = response.json()
        message = content.get("message", "")
    except json.JSONDecodeError:
        message = response.content
    return message


def _filter_credentials(error_message: str) -> str:
    credentials = f"{settings.EMS_API_USER}:{settings.EMS_API_PASSWORD}@"
    error_message = error_message.replace(credentials, "")
    return error_message
