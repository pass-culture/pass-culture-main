from functools import wraps
import typing

import flask

from pcapi import settings
from pcapi.models import api_errors
from pcapi.routes.adage.v1.blueprint import EAC_API_KEY_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


def adage_api_key_required(route_function: typing.Callable) -> typing.Callable:
    add_security_scheme(route_function, EAC_API_KEY_AUTH)

    @wraps(route_function)
    def wrapper(*args: typing.Any, **kwds: typing.Any) -> flask.Response:
        mandatory_authorization_type = "Bearer "
        authorization_header = flask.request.headers.get("Authorization")

        if not authorization_header or mandatory_authorization_type not in authorization_header:
            raise api_errors.UnauthorizedError(errors={"Authorization": ["Missing API key"]})

        adage_api_key = authorization_header.replace(mandatory_authorization_type, "")
        if adage_api_key != settings.EAC_API_KEY:
            raise api_errors.UnauthorizedError(errors={"Authorization": ["Wrong API key"]})

        return route_function(*args, **kwds)

    return wrapper
