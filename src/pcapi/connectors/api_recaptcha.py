import os

from pcapi.utils import requests


RECAPTCHA_API_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET")


def get_token_validation_and_score(token: str) -> dict:
    params = {"secret": RECAPTCHA_SECRET, "response": token}
    api_response = requests.post(RECAPTCHA_API_URL, data=params)
    json_response = api_response.json()

    return {
        "success": json_response.get("success"),
        "error-codes": json_response.get("error-codes", []),
        "score": json_response.get("score", 0),
        "action": json_response.get("action", ""),
    }
