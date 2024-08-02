"""
A client for the subcategory suggestion API.
Documentation of the API: https://compliance.passculture.team/latest/docs#
"""

from pcapi import settings
from pcapi.core.auth import api as auth_api
from pcapi.core.external.subcategory_suggestion_backends.base import BaseBackend
from pcapi.core.external.subcategory_suggestion_backends.base import MostProbableSubcategories
from pcapi.core.offerers.models import Venue
from pcapi.utils import requests


SUBCATEGORY_SUGGESTION_TIMEOUT_SECONDS = 3


class SubcategorySuggestionApiException(Exception):
    pass


class SubcategorySuggestionBackend(BaseBackend):
    def get_most_probable_subcategories(
        self, offer_name: str, offer_description: str | None = None, venue: Venue | None = None
    ) -> MostProbableSubcategories:
        url = settings.SUBCATEGORY_SUGGESTION_API_URL
        try:
            id_token = self.get_id_token_for_suggestion(settings.COMPLIANCE_API_CLIENT_ID)
        except:
            raise SubcategorySuggestionApiException("Couldn't get authentication token for subcategory suggestion API")
        headers = {
            "Authorization": f"Bearer {id_token}",
        }

        data = {
            "offer_name": offer_name,
            "offer_description": offer_description if offer_description else "",
            "venue_type_label": venue.venueTypeCode.value if venue else "",
            "offerer_name": venue.managingOfferer.name if venue else "",
        }
        response = requests.post(url, headers=headers, json=data, timeout=SUBCATEGORY_SUGGESTION_TIMEOUT_SECONDS)

        if response.status_code != 200:
            raise SubcategorySuggestionApiException(
                f"Error getting subcategory suggestion from API with code {response.status_code}"
            )
        try:
            results = MostProbableSubcategories(**response.json())
        except:
            raise SubcategorySuggestionApiException("Serialization failed while requesting subcategory suggestion API")

        return results

    def get_id_token_for_suggestion(self, client_id: str) -> str | None:
        return auth_api.get_id_token_from_google(client_id)
