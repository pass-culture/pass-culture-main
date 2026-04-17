import logging
import typing
from functools import wraps

import flask

from pcapi import settings
from pcapi.models import api_errors
from pcapi.serialization.spec_tree import add_security_scheme


BREVO_API_KEY_AUTH_NAME = "ApiKeyAuth"


logger = logging.getLogger(__name__)


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


def require_brevo_token_as_query_param(route_function: typing.Callable[..., typing.Any]) -> typing.Callable:
    """
    Use this decorator when the webhook should receive ?token=...

    API key is a better choice but there is no way to set authentication or custom headers in automations.
    require_brevo_token_as_query_param could be replaced with brevo_webhook when authentication is available for
    automation in Brevo UI (currently in Brevo roadmap).

    Less secured then API key so the secret is different.

    Routes should be protected by IP filtering, so errors should only alert about misconfiguration in Brevo UI.
    """

    @wraps(route_function)
    def validate_brevo_token(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:
        token = flask.request.args.get("token")
        if not token:
            logger.error("Missing token in Brevo webhook. Misconfigured?")
            raise api_errors.UnauthorizedError(errors={"auth": "token required"})

        if token != settings.BREVO_WEBHOOK_SECRET_QUERY_PARAM:
            logger.error("Wrong token in Brevo webhook. Misconfigured?")
            raise api_errors.UnauthorizedError(errors={"auth": "Invalid bearer token"})

        return route_function(*args, **kwargs)

    return validate_brevo_token
