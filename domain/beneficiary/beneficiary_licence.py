from connectors.api_recaptcha import validate_recaptcha_token


def is_licence_token_valid(token: str) -> bool:
    return validate_recaptcha_token(token)
