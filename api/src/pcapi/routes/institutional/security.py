from functools import wraps
import typing

import flask

from pcapi import settings
from pcapi.models import api_errors
from pcapi.serialization.spec_tree import add_security_scheme


INSTITUTIONAL_API_KEY_AUTH = "InstitutionalApiKeyAuth"


def institutional_api_key_required(route_function: typing.Callable) -> typing.Callable:
    """
    Require the request to provide a valid institutional API key.
    The key should be provided in the Authorization header with the Bearer scheme.
    """
    add_security_scheme(route_function, INSTITUTIONAL_API_KEY_AUTH)

    @wraps(route_function)
    def wrapper(*args: typing.Any, **kwds: typing.Any) -> flask.Response:
        mandatory_authorization_type = "Bearer "
        authorization_header = flask.request.headers.get("Authorization")

        if not settings.INSTITUTIONAL_API_KEY:
            raise ValueError("INSTITUTIONAL_API_KEY not defined")

        if not authorization_header or mandatory_authorization_type not in authorization_header:
            raise api_errors.UnauthorizedError(errors={"Authorization": ["Missing API key"]})

        institutional_api_key = authorization_header.replace(mandatory_authorization_type, "")
        if institutional_api_key != settings.INSTITUTIONAL_API_KEY:
            raise api_errors.UnauthorizedError(errors={"Authorization": ["Wrong API key"]})

        return route_function(*args, **kwds)

    return wrapper
