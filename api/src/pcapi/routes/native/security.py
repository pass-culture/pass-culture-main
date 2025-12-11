import logging
import typing
from functools import wraps

import sentry_sdk
from flask import g
from flask import request
from flask_jwt_extended.view_decorators import jwt_required
from flask_login import current_user

from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.native.blueprint import JWT_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)


RouteFunc = typing.Callable[..., typing.Any]
RouteDecorator = typing.Callable[..., typing.Any]


def authenticated_and_active_user_required(route_function: RouteFunc) -> RouteDecorator:
    add_security_scheme(route_function, JWT_AUTH)

    @wraps(route_function)
    @jwt_required()
    def retrieve_authenticated_user(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        setup_context()
        if not current_user.isActive:
            _raise_forbidden(current_user.email)
        return route_function(current_user, *args, **kwargs)

    return retrieve_authenticated_user


def authenticated_maybe_inactive_user_required(route_function: RouteFunc) -> RouteDecorator:
    add_security_scheme(route_function, JWT_AUTH)

    @wraps(route_function)
    @jwt_required()
    def retrieve_authenticated_user(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        setup_context()
        return route_function(current_user, *args, **kwargs)

    return retrieve_authenticated_user


def setup_context() -> None:
    if current_user.is_anonymous:
        _raise_forbidden(g.jwt_data.sub)

    # TODO rpa: is this still needed ?
    # the user is set in sentry in before_request, way before we do the
    # token auth so it needs to be also set here.
    sentry_sdk.set_user({"id": current_user.id})
    sentry_sdk.set_tag("device.id", request.headers.get("device-id", None))


def _raise_forbidden(user_email: str) -> None:
    logger.info("Authenticated user with email %s not found or inactive", user_email)
    raise ForbiddenError({"email": ["Utilisateur introuvable"]})
