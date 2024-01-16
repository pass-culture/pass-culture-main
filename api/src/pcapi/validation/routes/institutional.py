import functools
import typing

import flask

from pcapi import settings
from pcapi.models.api_errors import ForbiddenError


def require_institutional_api_token(route_function: typing.Callable[..., typing.Any]) -> typing.Callable:
    @functools.wraps(route_function)
    def validate_institutional_api_token(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:
        expected_authorization_header = f"Bearer {settings.INSTITUTIONAL_API_KEY}"
        if flask.request.headers.get("Authorization") != expected_authorization_header:
            errors = ForbiddenError()
            errors.add_error("token", "Invalid token")
            raise errors

        return route_function(*args, **kwargs)

    return validate_institutional_api_token
