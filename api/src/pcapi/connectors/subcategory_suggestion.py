"""
A client for the subcategory suggestion API.
Documentation of the API: https://compliance.passculture.team/latest/docs#
"""

from pcapi import settings
from pcapi.core.auth import api as auth_api
from pcapi.core.offerers.models import Venue
from pcapi.routes.serialization import BaseModel
from pcapi.utils import requests


SUBCATEGORY_SUGGESTION_TIMEOUT_SECONDS = 3


class SubcategorySuggestionApiException(Exception):
    pass


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
        id_token = dev_get_id_token_for_compliance(settings.COMPLIANCE_API_CLIENT_ID)
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


def dev_get_id_token_for_compliance(client_id: str) -> str | None:
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
        return None
    except Exception as exc:  # pylint: disable=broad-except
        return None
    return id_token
