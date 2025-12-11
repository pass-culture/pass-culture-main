import logging
import typing
from functools import wraps

from flask import g
from flask_login import current_user

from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import UnauthorizedError
from pcapi.routes.native.blueprint import JWT_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)


RouteFunc = typing.Callable[..., typing.Any]
RouteDecorator = typing.Callable[..., typing.Any]


def authenticated_and_active_user_required(route_function: RouteFunc) -> RouteDecorator:
    @wraps(route_function)
    @authenticated_maybe_inactive_user_required
    def retrieve_authenticated_user(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if not current_user.isActive:
            _raise_forbidden(current_user.email)
        return route_function(*args, **kwargs)

    return retrieve_authenticated_user


def authenticated_maybe_inactive_user_required(route_function: RouteFunc) -> RouteDecorator:
    add_security_scheme(route_function, JWT_AUTH)

    @wraps(route_function)
    def retrieve_authenticated_user(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if current_user.is_anonymous:
            if not getattr(g, "jwt_data", None):
                raise UnauthorizedError("Invalid token")
            _raise_forbidden(g.jwt_data.sub)
        return route_function(*args, **kwargs)

    return retrieve_authenticated_user


def _raise_forbidden(user_email: str) -> None:
    logger.info("Authenticated user with email %s not found or inactive", user_email)
    raise ForbiddenError({"email": ["Utilisateur introuvable"]})
