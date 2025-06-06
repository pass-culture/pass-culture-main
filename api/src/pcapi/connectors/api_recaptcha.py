from enum import Enum

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.utils import requests


class ReCaptchaVersion(Enum):
    V2 = "2"
    V3 = "3"


class ReCaptchaException(Exception):
    pass


class MissingReCaptchaTokenException(ReCaptchaException):
    pass


class InvalidRecaptchaTokenException(ApiErrors):
    def __init__(self, message: str = "Le token renseigné n'est pas valide"):
        super().__init__()
        self.add_error("token", message)


def get_token_validation_and_score(token: str, secret: str) -> dict:
    params = {"secret": secret, "response": token}
    try:
        api_response = requests.post(settings.RECAPTCHA_API_URL, data=params, log_info=False)
        api_response.raise_for_status()
        json_response = api_response.json()
    except requests.exceptions.RequestException as exc:
        raise ReCaptchaException() from exc

    return {
        "success": json_response.get("success"),
        "error-codes": json_response.get("error-codes", []),
        # V3 specific fields
        "score": json_response.get("score"),
        "action": json_response.get("action"),
    }


def check_recaptcha_token_is_valid(
    token: str | None,
    secret: str,
    version: ReCaptchaVersion,
    original_action: str | None = None,
    minimal_score: float | None = None,
) -> None:
    # This is to prevent E2E tests from being flaky
    if settings.RECAPTCHA_IGNORE_VALIDATION:
        return

    if not token:
        raise MissingReCaptchaTokenException()

    response = get_token_validation_and_score(token, secret)
    is_token_valid = response["success"]

    if not is_token_valid:
        errors_found = response["error-codes"]

        if errors_found == ["timeout-or-duplicate"]:
            raise InvalidRecaptchaTokenException()
        raise ReCaptchaException(f"Encountered the following error(s): {errors_found}")

    if version == ReCaptchaVersion.V3:
        if response["score"] < minimal_score:
            raise InvalidRecaptchaTokenException(
                f"Le token renseigné n'est pas valide : Le score ({response['score']}) est trop faible (requis : {minimal_score})"
            )

        if response["action"] != original_action:
            raise ReCaptchaException(
                f"The action '{response['action']}' does not match '{original_action}' from the form"
            )


def check_native_app_recaptcha_token(token: str | None) -> None:
    check_recaptcha_token_is_valid(token, settings.NATIVE_RECAPTCHA_SECRET, ReCaptchaVersion.V2)


def check_web_recaptcha_token(token: str | None, secret: str, original_action: str, minimal_score: float) -> None:
    check_recaptcha_token_is_valid(token, secret, ReCaptchaVersion.V3, original_action, minimal_score)
