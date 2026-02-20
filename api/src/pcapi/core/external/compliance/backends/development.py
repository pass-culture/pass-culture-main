import logging

from pcapi import settings
from pcapi.utils import requests

from .compliance import ComplianceBackend


logger = logging.getLogger(__name__)


class DevelopmentBackend(ComplianceBackend):
    def _get_id_token_for_compliance(self, client_id: str) -> str | None:
        # This is a fake auth_token; if you want to test it in development env
        # you have to use the result returned by 'gcloud auth print-access-token'
        auth_token = "gcloud auth print-access-token"

        try:
            id_token_response = requests.post(
                f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{settings.COMPLIANCE_API_SERVICE_ACCOUNT}:generateIdToken",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                json={"audience": client_id, "includeEmail": "true"},
            )
            id_token = id_token_response.json()["token"]
        except requests.exceptions.InvalidHeader:
            # The auth_token has probably not been changed to a correct value
            logger.info("Check the value of your auth_token")
            return None
        except Exception as exc:
            logger.info("Could not get id_token", extra={"exc": exc})
            return None
        return id_token
