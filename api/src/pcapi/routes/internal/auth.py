import functools
import typing

import flask
from flask import request

from pcapi import settings
from pcapi.models import api_errors


API_KEY_HEADER_NAME = "x-api-key"


def api_key_required(route_function: typing.Callable) -> typing.Callable:
    @functools.wraps(route_function)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:
        token = request.headers.get(API_KEY_HEADER_NAME)
        if not token:
            raise api_errors.UnauthorizedError(errors={"auth": "API key required"})

        if token != settings.E2E_API_KEY:
            raise api_errors.UnauthorizedError(errors={"auth": "Invalid API key"})

        return route_function(*args, **kwargs)

    return wrapper
