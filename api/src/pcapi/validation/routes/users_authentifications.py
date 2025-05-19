import logging
import typing
from functools import wraps

import flask
import sentry_sdk
from flask import _request_ctx_stack
from flask import g
from flask import request
from flask_login import current_user
from werkzeug.local import LocalProxy

from pcapi import settings
from pcapi.core.offerers.api import find_api_key
from pcapi.core.offerers.models import ApiKey
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import repository as users_repo
from pcapi.core.users.models import User
from pcapi.models import api_errors
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)

API_KEY_AUTH_NAME = "ApiKeyAuth"
COOKIE_AUTH_NAME = "SessionAuth"


def login_or_api_key_required(function: typing.Callable) -> typing.Callable:
    add_security_scheme(function, API_KEY_AUTH_NAME)
    add_security_scheme(function, COOKIE_AUTH_NAME)

    @wraps(function)
    def wrapper(*args: typing.Any, **kwds: typing.Any) -> flask.Response:
        _fill_current_api_key()
        basic_authentication()

        if not g.current_api_key and not current_user.is_authenticated:
            raise api_errors.UnauthorizedError(errors={"auth": "API key or login required"})
        if g.current_api_key:
            # The api using this decorator will be deprecated
            # log calls with an api_key, they are the only one not coming from our PRO front
            logger.info(
                "Call to CM v2 api",
                extra={"offerer_id": g.current_api_key.offerer.id, "offerer_name": g.current_api_key.offerer.name},
            )
            _check_active_offerer(g.current_api_key)
        return function(*args, **kwds)

    return wrapper


def brevo_webhook(route_function: typing.Callable) -> typing.Callable:
    add_security_scheme(route_function, API_KEY_AUTH_NAME)

    @wraps(route_function)
    def wrapper(*args: typing.Any, **kwds: typing.Any) -> flask.Response:
        mandatory_authorization_type = "Bearer "
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            raise api_errors.UnauthorizedError(errors={"auth": "API key required"})

        bearer = authorization_header.replace(mandatory_authorization_type, "")
        if bearer != settings.BREVO_WEBHOOK_SECRET:
            raise api_errors.UnauthorizedError(errors={"auth": "Invalid bearer token"})

        return route_function(*args, **kwds)

    return wrapper


def provider_api_key_required(route_function: typing.Callable) -> typing.Callable:
    """
    Require the user to be authenticated as a provider using an API key.

    Prevent old API key (that authenticates an offerer) bearer to access routes requiring an
    authenticated provider.
    """
    add_security_scheme(route_function, API_KEY_AUTH_NAME)

    @wraps(route_function)
    def wrapper(*args: typing.Any, **kwds: typing.Any) -> flask.Response:
        _fill_current_api_key()

        if not g.current_api_key:
            raise api_errors.UnauthorizedError(errors={"auth": "API key required"})

        if not g.current_api_key.provider:
            raise api_errors.UnauthorizedError(
                errors={"auth": "Deprecated API key. Please contact provider support to get a new API key"}
            )
        sentry_sdk.set_tag("provider-name", g.current_api_key.provider.name)
        sentry_sdk.set_tag("provider-id", g.current_api_key.provider.id)

        _check_active_offerer(g.current_api_key)
        _check_active_provider(g.current_api_key)
        return route_function(*args, **kwds)

    return wrapper


def _check_active_offerer(api_key: ApiKey) -> None:
    if not api_key.offerer.isActive:
        raise api_errors.ForbiddenError(errors={"auth": ["Inactive offerer"]})


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

        if g.current_api_key is not None:
            g.log_request_details_extra = {
                "public_api": {
                    "api_key": g.current_api_key.id,
                    "provider_id": g.current_api_key.providerId,
                }
            }


def _get_current_api_key() -> ApiKey | None:
    assert "current_api_key" in g, "Can only be used in a route wrapped with api_key_required"
    return g.current_api_key


current_api_key: ApiKey = LocalProxy(_get_current_api_key)  # type: ignore[assignment]


def basic_authentication() -> User | None:
    # `pcapi.utils.login_manager` cannot be imported at module-scope,
    # because the application context may not be available and that
    # module needs it.
    from pcapi.utils.login_manager import get_request_authorization

    auth = get_request_authorization()
    # According to the Werkzeug documentation auth.password is None
    # for any auth that is not basic auth.
    if not auth or not auth.password or auth.username is None:
        return None
    errors = api_errors.UnauthorizedError(www_authenticate="Basic")
    try:
        user = users_repo.get_user_with_credentials(auth.username, auth.password)
    except users_exceptions.InvalidIdentifier as exc:
        errors.add_error("identifier", "Identifiant ou mot de passe incorrect")
        raise errors from exc
    except users_exceptions.UnvalidatedAccount as exc:
        errors.add_error("identifier", "Ce compte n'est pas validé.")
        raise errors from exc
    logger.info(
        "User logged in with authorization header",
        extra={"route": str(request.url_rule), "username": auth.username, "avoid_current_user": True},
    )
    # push the user to the current context - similar to flask-login
    ctx = _request_ctx_stack.top
    ctx.user = user
    return user
