from pcapi.connectors.api_recaptcha import get_token_validation_and_score
from pcapi.models import ApiErrors


class ReCaptchaException(Exception):
    pass


class InvalidRecaptchaTokenException(ApiErrors):
    def __init__(self):
        super().__init__()
        self.add_error("token", "Le token renseigné n'est pas valide")


def check_recaptcha_token_is_valid(token: str, original_action: str, minimal_score: float) -> None:
    response = get_token_validation_and_score(token)
    is_token_valid = response.get("success")

    if not is_token_valid:
        errors_found = response.get("error-codes", [])

        if errors_found == ["timeout-or-duplicate"]:
            raise InvalidRecaptchaTokenException()
        else:
            raise ReCaptchaException(f"Encountered the following error(s): {errors_found}")

    response_score = response.get("score", 0)

    if response_score < minimal_score:
        raise InvalidRecaptchaTokenException()

    action = response.get("action", "")
    if action != original_action:
        raise ReCaptchaException(f"The action '{action}' does not match '{original_action}' from the form")
