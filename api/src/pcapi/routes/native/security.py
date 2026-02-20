import logging
import typing
from functools import wraps

import flask
import sentry_sdk
from flask_login import current_user
from flask_login import login_user

from pcapi.core.users import models as users_models
from pcapi.core.users import sessions as user_session_manager
from pcapi.models import db
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
            if not hasattr(flask.g, "jwt"):
                raise UnauthorizedError("Invalid token")
            _raise_forbidden(flask.g.jwt.data.sub)
        return route_function(*args, **kwargs)

    return retrieve_authenticated_user


def authenticated_with_refresh_token(route_function: RouteFunc) -> RouteDecorator:
    @wraps(route_function)
    def _authenticated_with_refresh_token(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        user_session_manager.load_jwt(
            request=flask.request,
            jwt_type=user_session_manager.JwtType.REFRESH,
        )

        if not hasattr(flask.g, "jwt"):
            raise UnauthorizedError("Invalid token")

        user = db.session.query(users_models.User).filter(users_models.User.email == flask.g.jwt.data.sub).one_or_none()
        if user:
            login_user(
                user,
                force=True,  # also accept users where isActive=False as needed for some features.
            )
            # the user is set in sentry in before_request, way before we do the
            # token auth so it needs to be also set here.
            sentry_sdk.set_user({"id": user.id})
        else:
            _raise_forbidden(flask.g.jwt.data.sub)

        return route_function(*args, **kwargs)

    return _authenticated_with_refresh_token


def _raise_forbidden(user_email: str) -> None:
    logger.info("Authenticated user with email %s not found or inactive", user_email)
    raise ForbiddenError({"email": ["Utilisateur introuvable"]})
