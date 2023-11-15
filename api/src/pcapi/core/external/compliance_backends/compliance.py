import logging

from pcapi import settings
from pcapi.core.auth import api as auth_api
from pcapi.core.external.compliance_backends.base import BaseBackend
from pcapi.tasks.serialization.compliance_tasks import GetComplianceScoreRequest
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class ComplianceBackend(BaseBackend):
    def get_score_from_compliance_api(self, payload: GetComplianceScoreRequest) -> tuple[int | None, list[str]]:
        client_id = settings.COMPLIANCE_API_CLIENT_ID

        id_token = self.get_id_token_for_compliance(client_id)
        if not id_token:  # only possible in development
            return None, []

        data = payload.to_dict()
        try:
            api_response = requests.post(
                "https://compliance.passculture.team/latest/model/compliance/scoring",
                headers={
                    "Authorization": f"Bearer {id_token}",
                    "accept": "application/json",
                },
                json=data,
            )

        except requests.exceptions.RequestException as exc:
            logger.exception("Connection to Compliance API failed", extra={"exc": exc})
            raise requests.ExternalAPIException(is_retryable=True) from exc

        if not api_response.ok:
            if api_response.status_code in {401, 403}:
                logger.exception(
                    "Connection to Compliance API was refused",
                    extra={"status_code": api_response.status_code},
                )
                raise requests.ExternalAPIException(is_retryable=False)
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

        data = api_response.json()
        return data["probability_validated"], data.get("rejection_main_features", [])

    def get_id_token_for_compliance(self, client_id: str) -> str | None:
        return auth_api.get_id_token_from_google(client_id)
