import typing
from functools import wraps

import flask

from pcapi import settings
from pcapi.models import api_errors
from pcapi.serialization.spec_tree import add_security_scheme


BREVO_API_KEY_AUTH_NAME = "ApiKeyAuth"


def brevo_webhook(route_function: typing.Callable) -> typing.Callable:
    add_security_scheme(route_function, BREVO_API_KEY_AUTH_NAME)

    @wraps(route_function)
    def wrapper(*args: typing.Any, **kwds: typing.Any) -> flask.Response:
        mandatory_authorization_type = "Bearer "
        authorization_header = flask.request.headers.get("Authorization")
        if not authorization_header:
            raise api_errors.UnauthorizedError(errors={"auth": "API key required"})

        bearer = authorization_header.replace(mandatory_authorization_type, "")
        if bearer != settings.BREVO_WEBHOOK_SECRET:
            raise api_errors.UnauthorizedError(errors={"auth": "Invalid bearer token"})

        return route_function(*args, **kwds)

    return wrapper
