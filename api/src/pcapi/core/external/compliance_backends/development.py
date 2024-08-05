import logging

from pcapi import settings
from pcapi.core.external import utils

from .compliance import ComplianceBackend


logger = logging.getLogger(__name__)


class DevelopmentBackend(ComplianceBackend):
    def get_id_token_for_compliance(self, client_id: str) -> str | None:
        # This is a fake auth_token; if you want to test it in development env
        # you have to use the result returned by 'gcloud auth print-access-token'
        auth_token = "gcloud auth print-access-token"
        api_service_account = settings.COMPLIANCE_API_SERVICE_ACCOUNT
        return utils.get_id_token(client_id, auth_token, api_service_account)
