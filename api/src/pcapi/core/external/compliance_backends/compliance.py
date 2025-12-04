import logging

from pcapi import settings
from pcapi.core.auth import api as auth_api
from pcapi.core.external.compliance_backends.base import BaseBackend
from pcapi.tasks.serialization.compliance_tasks import CompliancePredictionOutput
from pcapi.tasks.serialization.compliance_tasks import GetComplianceScoreRequest
from pcapi.utils import requests


logger = logging.getLogger(__name__)
COMPLIANCE_DOMAIN = "https://compliance.passculture.team"


class ComplianceBackend(BaseBackend):
    def get_score_from_compliance_api(self, payload: GetComplianceScoreRequest) -> CompliancePredictionOutput | None:
        data = self._post(
            route="/latest/model/compliance/scoring",
            payload=payload.to_dict(),
        )
        if data:
            return CompliancePredictionOutput.parse_obj(data)

        return None

    def _post(self, route: str, payload: dict) -> dict | None:
        id_token = auth_api.get_id_token_from_google(settings.COMPLIANCE_API_CLIENT_ID)
        if not id_token:  # only possible in development
            return None

        try:
            api_response = requests.post(
                f"{COMPLIANCE_DOMAIN}{route}",
                headers={
                    "Authorization": f"Bearer {id_token}",
                    "accept": "application/json",
                },
                json=payload,
                log_info=False,
            )

        except requests.exceptions.RequestException as exc:
            logger.exception("Connection to Compliance API failed", extra={"exc": exc})
            raise requests.ExternalAPIException(is_retryable=True) from exc

        if not api_response.ok:
            self._handle_errors(api_response)

        return api_response.json()

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
                error_data += api_response.json()
            except requests.exceptions.JSONDecodeError:  # docs says response should be a json, but let's be careful
                pass

            logger.exception(
                "Data sent to Compliance API is faulty",
                extra=error_data,
            )
            raise requests.ExternalAPIException(is_retryable=False)

        error_data = {"status_code": api_response.status_code}
        try:
            error_data += api_response.json()
        except requests.exceptions.JSONDecodeError:
            pass
        logger.exception(
            "Response from Compliance API is not ok",
            extra=error_data,
        )
        raise requests.ExternalAPIException(is_retryable=True)
