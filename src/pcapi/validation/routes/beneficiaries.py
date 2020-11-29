from flask import Request

from pcapi.models.api_errors import ApiErrors


def check_verify_licence_token_payload(payload: Request) -> None:
    try:
        token = payload.get_json()["token"]
    except:
        errors = ApiErrors()
        errors.add_error("token", "Missing token")
        raise errors
    if not token or token == "null":
        errors = ApiErrors()
        errors.add_error("token", "Empty token")
        raise errors
