import datetime
import enum
import json
import logging
from typing import Any

from pydantic import parse_obj_as

from pcapi import settings
from pcapi.connectors.serialization.boost_serializers import LoginBoost
from pcapi.core.external_bookings.boost.exceptions import BoostAPIException
from pcapi.core.providers.models import BoostCinemaDetails
import pcapi.core.providers.repository as providers_repository
from pcapi.repository import repository
from pcapi.routes.serialization import BaseModel
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class ResourceBoost(enum.Enum):
    if settings.IS_RUNNING_TESTS:
        EXAMPLE = "example"
        EXAMPLE_WITH_PATTERNS = "example/{start}/{end}"
    FILMS = "api/films"
    SHOWTIMES = "api/showtimes"
    SHOWTIME = "api/showtimes/{id}"
    COMPLETE_SALE = "api/sale/complete"


LOGIN_ENDPOINT = "api/vendors/login"


def build_url(cinema_url: str, resource: ResourceBoost, pattern_values: dict[str, Any] | None = None) -> str:
    resource_url = resource.value
    if pattern_values:
        for key, value in pattern_values.items():
            resource_url = resource_url.replace("{" + key + "}", str(value))
    return f"{cinema_url}{resource_url}"


def login(cinema_details: BoostCinemaDetails, ignore_device: bool = False) -> str:
    """
    This will provide a JWT for authenticated calls to Boost API.
    The token has a duration of 24 hours, and is saved in DB along its expiration date.
    """
    auth_payload = {
        "username": cinema_details.username,
        "password": cinema_details.password,
    }
    url = cinema_details.cinemaUrl + LOGIN_ENDPOINT
    request_date = datetime.datetime.utcnow()
    try:
        response = requests.post(url=url, json=auth_payload, params={"ignore_device": ignore_device})
    except requests.exceptions.RequestException as exc:
        logger.exception("Network error on Boost API", extra={"exc": exc, "url": url})
        raise BoostAPIException(f"Network error on Boost API: {url}") from exc

    if response.status_code != 200:
        try:
            content = response.json()
            message = content.get("message", "")
        except json.JSONDecodeError:
            message = response.content
        raise BoostAPIException(
            f"Unexpected {response.status_code} response from Boost API on {response.request.url}: {message}"
        )

    content = response.json()
    login_info = parse_obj_as(LoginBoost, content)
    token = login_info.token
    if not token:
        raise BoostAPIException("No token received from Boost API")
    cinema_details.token = token
    cinema_details.tokenExpirationDate = request_date + datetime.timedelta(hours=24)
    repository.save(cinema_details)
    return token


def headers(token: str) -> dict[str, str]:
    return {"Authorization": "Bearer " + token}


def check_token_validity(cinema_details: BoostCinemaDetails) -> bool:
    token = cinema_details.token
    token_expiration_date = cinema_details.tokenExpirationDate
    return bool(token and token_expiration_date and datetime.datetime.utcnow() < token_expiration_date)


def get_resource(
    cinema_str_id: str,
    resource: ResourceBoost,
    params: dict[str, Any] | None = None,
    pattern_values: dict[str, Any] | None = None,
) -> dict | list[dict] | list:
    cinema_details = providers_repository.get_boost_cinema_details(cinema_str_id)
    token = cinema_details.token if check_token_validity(cinema_details) else login(cinema_details)
    assert token  # for typing
    if params:
        response = requests.get(
            url=build_url(cinema_details.cinemaUrl, resource, pattern_values), headers=headers(token), params=params
        )
    else:
        response = requests.get(
            url=build_url(cinema_details.cinemaUrl, resource, pattern_values), headers=headers(token)
        )

    _check_response_is_ok(response, token, f"GET {resource}")

    return response.json()


def put_resource(cinema_str_id: str, resource: ResourceBoost, body: BaseModel) -> dict | list[dict] | list | None:
    cinema_details = providers_repository.get_boost_cinema_details(cinema_str_id)
    token = cinema_details.token if check_token_validity(cinema_details) else login(cinema_details)
    assert token  # for typing
    response = requests.put(
        url=build_url(cinema_details.cinemaUrl, resource), headers=headers(token), data=body.json(by_alias=True)
    )

    _check_response_is_ok(response, token, f"PUT {resource}")

    response_headers = response.headers.get("Content-Type")
    if response_headers and "application/json" in response_headers:
        return response.json()
    return None


def post_resource(cinema_str_id: str, resource: ResourceBoost, body: BaseModel) -> dict | list[dict] | list | None:
    cinema_details = providers_repository.get_boost_cinema_details(cinema_str_id)
    token = cinema_details.token if check_token_validity(cinema_details) else login(cinema_details)
    assert token  # for typing
    response = requests.post(
        url=build_url(cinema_details.cinemaUrl, resource), headers=headers(token), data=body.json(by_alias=True)
    )

    _check_response_is_ok(response, token, f"POST {resource}")

    response_headers = response.headers.get("Content-Type")
    if response_headers and "application/json" in response_headers:
        return response.json()
    return None


def _check_response_is_ok(response: requests.Response, cinema_api_token: str | None, request_detail: str) -> None:
    if response.status_code >= 400:
        reason = _extract_reason_from_response(response)
        message = _extract_message_from_response(response)
        error_message = _filter_token(reason, cinema_api_token)
        raise BoostAPIException(f"Error on Boost API on {request_detail} : {error_message} - {message}")


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


def _extract_message_from_response(response: requests.Response) -> str:
    try:
        content = response.json()
        message = content.get("message", "")
    except json.JSONDecodeError:
        message = response.content
    return message


def _filter_token(error_message: str, token: str | None) -> str:
    if isinstance(token, str) and token in error_message:
        error_message = error_message.replace(token, "")
    return error_message
