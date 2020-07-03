from flask import Request
from models.api_errors import ApiErrors


def check_verify_licence_token_payload(payload: Request) -> None:
    try:
        payload.get_json()['token']
    except:
        errors = ApiErrors()
        errors.add_error('token', "Missing token")
        raise errors


def check_licence_token_is_valid(token: str) -> bool:
    return token == 'authorized-token'

def check_application_update_payload(payload: Request) -> None:
    try:
        payload.get_json()['id']
    except:
        errors = ApiErrors()
        errors.add_error('id', "Missing key id")
        raise errors

def parse_application_id(application_id: str) -> int:
    try:
        return int(application_id)
    except:
        errors = ApiErrors()
        errors.add_error('id', "Not a number")
        raise errors
