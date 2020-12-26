from pcapi import settings
from pcapi.utils import requests


def get_token_validation_and_score(token: str) -> dict:
    params = {"secret": settings.RECAPTCHA_SECRET, "response": token}
    api_response = requests.post(settings.RECAPTCHA_API_URL, data=params)
    json_response = api_response.json()

    return {
        "success": json_response.get("success"),
        "error-codes": json_response.get("error-codes", []),
        "score": json_response.get("score", 0),
        "action": json_response.get("action", ""),
    }
