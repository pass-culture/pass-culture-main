import logging

from pcapi import settings
from pcapi.core.external import utils

from .subcategory_suggestion import SubcategorySuggestionBackend


logger = logging.getLogger(__name__)


class DevelopmentBackend(SubcategorySuggestionBackend):
    def get_id_token_for_suggestion(self, client_id: str) -> str | None:
        auth_token = settings.SUBCATEGORY_SUGGESTION_LOCAL_TOKEN
        api_service_account = settings.COMPLIANCE_API_SERVICE_ACCOUNT
        return utils.get_id_token(client_id, auth_token, api_service_account)
