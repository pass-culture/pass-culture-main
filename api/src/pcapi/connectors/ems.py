"""
EMS connectors that handle schedule & booking APIs from this provider.
"""

import hmac
import json
import logging

import pydantic.v1 as pydantic_v1
import sentry_sdk
from requests.auth import HTTPBasicAuth  # noqa: TID251

from pcapi import settings
from pcapi.connectors.serialization import ems_serializers
from pcapi.core.external_bookings.ems.exceptions import EMSAPIException
from pcapi.core.external_bookings.exceptions import ExternalBookingSoldOutError
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class AbstractEMSConnector:
    def __init__(self, enable_debug: bool = False):
        super().__init__()
        self.enable_debug = enable_debug or settings.ENABLE_CINEMA_PROVIDER_DEBUG

    def build_url(self) -> str:
        raise NotImplementedError

    def build_query_params(self, version: int) -> dict:
        return {"version": version}

    def build_auth(self) -> HTTPBasicAuth:
        auth = HTTPBasicAuth(username=settings.EMS_API_USER, password=settings.EMS_API_PASSWORD)
        return auth

    def _check_response_is_ok(self, response: requests.Response) -> None:
        if response.status_code >= 400:
            reason = self._extract_reason_from_response(response)
            message = self._extract_message_from_response(response)
            raise EMSAPIException(f"Error on EMS API call {reason} - {message}")

    def _extract_reason_from_response(self, response: requests.Response) -> str:
        if isinstance(response.reason, bytes):
            try:
                reason = response.reason.decode("utf-8")
            except UnicodeDecodeError:
                reason = response.reason.decode("iso-8859-1")
        else:
            reason = response.reason
        return reason

    def _extract_message_from_response(self, response: requests.Response) -> str:
        try:
            content = response.json()
            message = content.get("message", "")
        except requests.exceptions.JSONDecodeError:
            message = response.content
        return message


class EMSScheduleConnector(AbstractEMSConnector):
    def build_url(self) -> str:
        return settings.EMS_API_URL

    def get_schedules(self, version: int = 0) -> ems_serializers.ScheduleResponse:
        response = requests.get(
            url=self.build_url(),
            auth=self.build_auth(),
            params=self.build_query_params(version),
            timeout=settings.EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
        )

        if self.enable_debug:
            logger.debug(
                "[CINEMA] Call to external API",
                extra={
                    "api_client": "EMSScheduleConnector",
                    "method": "get_schedules",
                    "method_params": {"version": version},
                    "response": response.json(),
                },
            )

        self._check_response_is_ok(response)
        return pydantic_v1.parse_obj_as(ems_serializers.ScheduleResponse, response.json())

    def get_movie_poster_from_api(self, image_url: str) -> bytes:
        api_response = requests.get(image_url, timeout=settings.EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS)

        if api_response.status_code != 200:
            raise EMSAPIException(
                f"Error getting EMS API movie poster {image_url} with code {api_response.status_code}"
            )

        return api_response.content


class EMSSitesConnector(AbstractEMSConnector):
    def build_url(self) -> str:
        return settings.EMS_SITES_API_URL

    def get_available_sites(self, version: int = 0) -> list[ems_serializers.Site]:
        response = requests.get(
            url=self.build_url(),
            auth=self.build_auth(),
            params=self.build_query_params(version),
            timeout=settings.EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
        )

        if self.enable_debug:
            logger.debug(
                "[CINEMA] Call to external API",
                extra={
                    "api_client": "EMSSitesConnector",
                    "method": "get_available_sites",
                    "method_params": {"version": version},
                    "response": response.json(),
                },
            )

        self._check_response_is_ok(response)
        serialized_site_response = pydantic_v1.parse_obj_as(ems_serializers.SitesResponse, response.json())
        return serialized_site_response.sites


class EMSBookingConnector:
    digest_mode = "sha512"
    get_ticket_endpoint = "STATUT"
    booking_endpoint = "VENTE"
    shows_availability_endpoint = "SEANCE"
    cancelation_endpoint = "ANNULATION"

    def do_request(self, endpoint: str, payload: dict, request_timeout: int | None = None) -> requests.Response:
        """
        Perform the actual request, using mandatory headers
        and hashed payload.
        """
        sentry_sdk.set_tag("ems_http_call", endpoint)

        headers = self._build_headers()
        url = self._build_url(endpoint, payload)
        return requests.post(url, headers=headers, json=payload, timeout=request_timeout)

    def raise_for_status(self, response: requests.Response) -> None:
        response.raise_for_status()
        content = response.json()

        if not content and response.status_code == 200:
            # EMS return an empty response when cancelling instead of there usual ones
            # So we are forced to assume that empty response + 200 status code means we are ok
            return

        if content.get("statut") != 1:
            if content["code_erreur"] == 104:
                raise ExternalBookingSoldOutError
            raise EMSAPIException(f"Error on EMS API with {content['code_erreur']} - {content['message_erreur']}")

    def _build_headers(self) -> dict[str, str]:
        """
        Mandatory header to go through EMS API
        """
        return {"Source": settings.EMS_API_BOOKING_HEADER, "Content-Type": "application/json"}

    def _build_url(self, endpoint: str, payload: dict) -> str:
        """
        Build the url for EMS booking API according to their specifications.

        The payload that is going to be sent is also hashed with sha512 and a secret key
        and will be concatenate to the url we are calling.

        Args:
            endpoint (str): Endpoint we want to call (SEANCE, VENTE, ANNULATION, ...)
            payload (dict): Payload that is going to be sent

        Returns:
            url (str): Something like
                https://EMS_API_BOOKING_URL/ENDPOINT/digest/

        """
        # We can't just do str(payload) here
        # Because on EMS side they will hash our payload as well
        # and hash(str(payload)) != hash(json.dumps(payload))
        # (because '{"key": "value"}' is not "{'key': 'value'}")
        # So we need to hash exactly what we are sending
        # which are data as json format
        payload_stringify = json.dumps(payload)

        secret_key = settings.EMS_API_BOOKING_SECRET_KEY

        h = hmac.new(secret_key.encode(), digestmod=self.digest_mode)
        h.update(payload_stringify.encode())

        digest = h.hexdigest()

        return f"{settings.EMS_API_BOOKING_URL}{endpoint}/{digest}"
