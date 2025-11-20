import logging
import typing
from functools import wraps

import flask
import sentry_sdk
from flask import g
from flask import request
from werkzeug.local import LocalProxy

from pcapi.core.offerers.api import find_api_key
from pcapi.core.offerers.models import ApiKey
from pcapi.models import api_errors
from pcapi.routes.public import utils as public_utils
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)

API_KEY_AUTH_NAME = "ApiKeyAuth"


def api_key_required(route_function: typing.Callable) -> typing.Callable:
    """
    Require the user to be authenticated as a provider using an API key
    """
    add_security_scheme(route_function, API_KEY_AUTH_NAME)

    @wraps(route_function)
    def wrapper(*args: typing.Any, **kwds: typing.Any) -> flask.Response:
        _fill_current_api_key()
        public_utils.setup_public_api_log_extra(route_function)

        if not g.current_api_key:
            raise api_errors.UnauthorizedError(errors={"auth": "API key required"})

        sentry_sdk.set_tag("provider-name", g.current_api_key.provider.name)
        sentry_sdk.set_tag("provider-id", g.current_api_key.provider.id)

        _check_active_provider(g.current_api_key)
        return route_function(*args, **kwds)

    return wrapper


def _check_active_provider(api_key: ApiKey) -> None:
    if not api_key.provider.isActive:
        raise api_errors.ForbiddenError(errors={"auth": ["Inactive provider"]})


def _fill_current_api_key() -> None:
    mandatory_authorization_type = "Bearer "
    authorization_header = request.headers.get("Authorization")
    g.current_api_key = None

    if authorization_header and mandatory_authorization_type in authorization_header:
        app_authorization_credentials = authorization_header.replace(mandatory_authorization_type, "")
        g.current_api_key = find_api_key(app_authorization_credentials)


def _get_current_api_key() -> ApiKey | None:
    assert "current_api_key" in g, "Can only be used in a route wrapped with api_key_required"
    return g.current_api_key


current_api_key: ApiKey = LocalProxy(_get_current_api_key)  # type: ignore[assignment]
