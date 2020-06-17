from flask import request
from typing import Dict

from models.api_errors import ApiErrors


def check_licence_token_webhook_payload(payload: Dict):
    try:
        request.get_json()['token']
    except:
        errors = ApiErrors()
        errors.add_error('token', "Missing token")
        raise errors


def check_licence_token_is_valid(token):
    return token == 'authorized-token'
