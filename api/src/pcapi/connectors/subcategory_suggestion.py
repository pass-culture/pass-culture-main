"""
A client for the subcategory suggestion API.
Documentation of the API: https://compliance.passculture.team/latest/docs#
"""

from typing import TypedDict

from pcapi import settings
from pcapi.core.auth import api as auth_api
from pcapi.core.offerers.models import Venue
from pcapi.routes.serialization import BaseModel
from pcapi.utils import requests


SUBCATEGORY_SUGGESTION_TIMEOUT_SECONDS = 3


class SubcategorySuggestionApiException(Exception):
    pass


class PostSubcategorySuggestionBodyModel(TypedDict):
    offer_name: str
    offer_description: str | None
    venue_type_label: str | None
    offerer_name: str | None


class SubcategoryProbability(BaseModel):
    subcategory: str
    probability: float


class MostProbableSubcategories(BaseModel):
    most_probable_subcategories: list[SubcategoryProbability]


def get_suggested_categories(
    offer_name: str, offer_description: str | None = None, venue: Venue | None = None
) -> MostProbableSubcategories | None:
    """
    Returns the 3 most probable subcategories given an offer name, description and the venue type and offerer name
    """
    url = settings.SUBCATEGORY_SUGGESTION_API_URL
    id_token = auth_api.get_id_token_from_google(settings.COMPLIANCE_API_CLIENT_ID)
    if not id_token:  # id_token is None only in development
        return None
    headers = {
        "Authorization": f"Bearer {id_token}",
    }

    data = PostSubcategorySuggestionBodyModel(
        offer_name=offer_name,
        offer_description=offer_description,
        venue_type_label=venue.venueTypeCode.value if venue else None,
        offerer_name=venue.managingOfferer.name if venue else None,
    )
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
