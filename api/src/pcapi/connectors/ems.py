"""
EMS connectors that handle schedule & booking APIs from this provider.
"""

import hmac
import json

from pydantic import parse_obj_as
from requests import Response
from requests.auth import HTTPBasicAuth

from pcapi import settings
from pcapi.connectors.serialization import ems_serializers
from pcapi.connectors.serialization.ems_serializers import ScheduleResponse
from pcapi.core.external_bookings.ems.exceptions import EMSAPIException
from pcapi.utils import requests


class EMSScheduleConnector:
    def _build_url(self) -> str:
        return settings.EMS_API_URL

    def _build_query_params(self, version: int) -> dict:
        return {"version": version}

    def _build_auth(self) -> HTTPBasicAuth:
        auth = HTTPBasicAuth(username=settings.EMS_API_USER, password=settings.EMS_API_PASSWORD)
        return auth

    def get_schedules(self, version: int = 0) -> ScheduleResponse:
        response = requests.get(
            url=self._build_url(), auth=self._build_auth(), params=self._build_query_params(version)
        )

        self._check_response_is_ok(response)
        return parse_obj_as(ems_serializers.ScheduleResponse, response.json())

    def get_movie_poster_from_api(self, image_url: str) -> bytes:
        api_response = requests.get(image_url)

        if api_response.status_code != 200:
            raise EMSAPIException(
                f"Error getting EMS API movie poster {image_url} with code {api_response.status_code}"
            )

        return api_response.content

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
        except json.JSONDecodeError:
            message = response.content
        return message


class EMSBookingConnector:
    digest_mode = "sha512"
    booking_endpoint = "VENTE"

    def do_request(self, endpoint: str, payload: dict) -> Response:
        """
        Perform the actual request, using mandatory headers
        and hashed payload.
        """
        headers = self._build_headers()
        url = self._build_url(endpoint, payload)
        return requests.post(url, headers=headers, json=payload)

    def raise_for_status(self, response: Response) -> None:
        response.raise_for_status()
        content = response.json()
        if content.get("statut") != 1:
            raise EMSAPIException(f'Error on EMS API with {content["code_erreur"]} - {content["message_erreur"]}')

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
