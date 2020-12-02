import os

from pcapi.models import ApiErrors
from pcapi.utils import requests


RECAPTCHA_API_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET")


class ReCaptchaException(Exception):
    pass


class InvalidRecaptchaTokenException(ApiErrors):
    def __init__(self):
        super().__init__()
        self.add_error("token", "Le token renseigné n'est pas valide")


def check_recaptcha_token_is_valid(token: str, original_action: str, minimal_score: float) -> bool:
    if not token:
        return False

    params = {"secret": RECAPTCHA_SECRET, "response": token}
    api_response = requests.post(RECAPTCHA_API_URL, data=params)

    json_response = api_response.json()
    is_token_valid = json_response.get("success")

    if not is_token_valid:
        errors_found = json_response.get("error-codes", [])

        if errors_found == ["timeout-or-duplicate"]:
            raise InvalidRecaptchaTokenException()
        else:
            raise ReCaptchaException(f"Encountered the following error(s): {errors_found}")

    response_score = json_response.get("score", 0)

    if response_score < minimal_score:
        raise ReCaptchaException(f"Token score is too low ({response_score}) to match minimum score ({minimal_score})")

    action = json_response.get("action", "")
    if action != original_action:
        raise ReCaptchaException(f"The action '{action}' does not match '{original_action}' from the form")
