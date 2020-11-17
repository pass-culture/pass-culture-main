import os

from pcapi.connectors.api_recaptcha import validate_recaptcha_token

from pcapi.models.api_errors import ApiErrors

# FIXME(cgaunet, 2020-11-17): change the required score once we have data on production environment
RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE = float(os.environ.get("RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE", 0.0))


def validate_reset_password_token(token: str):
    token_is_valid = validate_recaptcha_token(token, "resetPassword", RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE)
    if not token_is_valid:
        errors = ApiErrors()
        errors.add_error("token", "Le token renseigné n'est pas valide")
        raise errors
