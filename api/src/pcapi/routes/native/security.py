from functools import wraps
import logging
import typing

from flask import _request_ctx_stack
from flask import request
from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
import sentry_sdk

from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.native.v1.blueprint import JWT_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)


RouteFunc = typing.Callable[..., typing.Any]
RouteDecorator = typing.Callable[..., typing.Any]


def authenticated_and_active_user_required(route_function: RouteFunc) -> RouteDecorator:
    add_security_scheme(route_function, JWT_AUTH)

    @wraps(route_function)
    @jwt_required()
    def retrieve_authenticated_user(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        user = setup_context()
        return route_function(user, *args, **kwargs)

    return retrieve_authenticated_user


def authenticated_maybe_inactive_user_required(route_function: RouteFunc) -> RouteDecorator:
    add_security_scheme(route_function, JWT_AUTH)

    @wraps(route_function)
    @jwt_required()
    def retrieve_authenticated_user(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        user = setup_context(must_be_active=False)
        return route_function(user, *args, **kwargs)

    return retrieve_authenticated_user


def setup_context(must_be_active: bool = True) -> User:
    email = get_jwt_identity()
    user = find_user_by_email(email)

    if must_be_active:
        invalid_user = user is None or not user.isActive
    else:
        invalid_user = user is None

    if invalid_user:
        logger.info("Authenticated user with email %s not found or inactive", email)
        raise ForbiddenError({"email": ["Utilisateur introuvable"]})

    user = typing.cast(User, user)

    # push the user to the current context - similar to flask-login
    ctx = _request_ctx_stack.top
    ctx.user = user

    # the user is set in sentry in before_request, way before we do the
    # token auth so it needs to be also set here.
    sentry_sdk.set_user({"id": user.id})
    sentry_sdk.set_tag("device.id", request.headers.get("device-id", None))

    return user
