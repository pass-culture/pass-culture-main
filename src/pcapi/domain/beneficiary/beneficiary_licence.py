import os

from pcapi.connectors.api_recaptcha import check_recaptcha_token_is_valid


RECAPTCHA_LICENCE_MINIMAL_SCORE = float(os.environ.get("RECAPTCHA_LICENCE_MINIMAL_SCORE", 0.5))


def is_licence_token_valid(token: str) -> bool:
    return check_recaptcha_token_is_valid(token, "submit", RECAPTCHA_LICENCE_MINIMAL_SCORE)
