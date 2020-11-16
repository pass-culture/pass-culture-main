import os

from pcapi.connectors.api_recaptcha import validate_recaptcha_token


RECAPTCHA_REQUIRED_SCORE = float(os.environ.get("RECAPTCHA_REQUIRED_SCORE", 0.5))


def is_licence_token_valid(token: str) -> bool:
    return validate_recaptcha_token(token, "submit", RECAPTCHA_REQUIRED_SCORE)
