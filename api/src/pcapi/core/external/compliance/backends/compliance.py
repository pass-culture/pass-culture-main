import datetime
import json
import logging

import google.auth
from google.cloud import iam_credentials_v1

from pcapi import settings
from pcapi.core.external.compliance import serialization
from pcapi.core.external.compliance.backends.base import BaseBackend
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class ComplianceBackend(BaseBackend):
    def get_score_from_compliance_api(
        self, payload: serialization.UpdateOfferComplianceScorePayload
    ) -> serialization.CompliancePredictionOutput | None:
        data = self._post(
            route="/latest/model/compliance/scoring",
            payload=payload.model_dump(),
        )
        if data:
            return serialization.CompliancePredictionOutput.model_validate(data)

        return None

    def search_offers(self, payload: serialization.SearchOffersRequest) -> serialization.SearchOffersResponse | None:
        data = self._post(
            route="/latest/search_edito/search",
            payload=payload.model_dump(),
        )
        if data:
            return serialization.SearchOffersResponse.model_validate(data)

        return None

    def _post(self, route: str, payload: dict) -> dict | None:
        target_service_account = settings.SA_API_COMPLIANCE_IAP
        if not target_service_account:
            logger.warning("SA_API_COMPLIANCE_IAP is not set, cannot call Compliance API")
            return None

        full_endpoint_url = f"{settings.COMPLIANCE_DOMAIN}{route}"
        try:
            id_token = self._get_signed_jwt(
                target_service_account=target_service_account, resource_url=full_endpoint_url
            )
        except Exception as exc:
            logger.exception("Failed to generate signed JWT for Compliance API", extra={"exc": exc})
            return None

        try:
            api_response = requests.post(
                full_endpoint_url,
                headers={
                    "Authorization": f"Bearer {id_token}",
                    "accept": "application/json",
                },
                json=payload,
                log_info=False,
                timeout=55,
            )

        except requests.exceptions.RequestException as exc:
            logger.exception("Connection to Compliance API failed", extra={"exc": exc})
            raise requests.ExternalAPIException(is_retryable=True) from exc

        if not api_response.ok:
            self._handle_errors(api_response)

        return api_response.json()

    def _get_signed_jwt(self, target_service_account: str, resource_url: str) -> str:
        iat = datetime.datetime.now(tz=datetime.timezone.utc)
        exp = iat + datetime.timedelta(seconds=3600)

        payload = {
            "iss": target_service_account,
            "sub": target_service_account,
            "aud": resource_url,
            "iat": int(iat.timestamp()),
            "exp": int(exp.timestamp()),
        }

        source_credentials, _ = google.auth.default()
        iam_client = iam_credentials_v1.IAMCredentialsClient(credentials=source_credentials)

        name = iam_client.service_account_path("-", target_service_account)
        response = iam_client.sign_jwt(name=name, payload=json.dumps(payload))

        return response.signed_jwt

    def _handle_errors(self, api_response: requests.Response) -> None:
        if api_response.status_code in {401, 403}:
            logger.exception(
                "Connection to Compliance API was refused",
                extra={"status_code": api_response.status_code},
            )
            # FIXME (prouzet, 2024-11-29) We experience random HTTP 403 errors (1 to 5 every day), so make them
            #  retryable until the issue is fixed on data team side. Sentry issue: 1613833
            raise requests.ExternalAPIException(is_retryable=(api_response.status_code == 403))

        if api_response.status_code == 422:
            error_data = {"status_code": api_response.status_code}
            try:
                error_data |= api_response.json()
            except requests.exceptions.JSONDecodeError:  # docs says response should be a json, but let's be careful
                pass

            logger.exception(
                "Data sent to Compliance API is faulty",
                extra=error_data,
            )
            raise requests.ExternalAPIException(is_retryable=False)

        error_data = {"status_code": api_response.status_code}
        try:
            error_data |= api_response.json()
        except requests.exceptions.JSONDecodeError:
            pass

        logger.exception(
            "Response from Compliance API is not ok",
            extra=error_data,
        )
        raise requests.ExternalAPIException(is_retryable=True)
