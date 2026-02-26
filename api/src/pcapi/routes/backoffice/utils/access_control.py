import logging
import typing
from functools import wraps

from flask import Response as FlaskResponse
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user

from pcapi.core.permissions import models as perm_models
from pcapi.models.api_errors import ApiErrors


logger = logging.getLogger(__name__)


class UnauthenticatedUserError(Exception):
    pass


def has_current_user_permission(permission: perm_models.Permissions | str) -> bool:
    if isinstance(permission, str):
        permission = perm_models.Permissions[permission]
    return permission in current_user.backoffice_profile.permissions


def _check_any_permission_of(permissions: typing.Iterable[perm_models.Permissions]) -> None:
    if not current_user.is_authenticated:
        raise UnauthenticatedUserError()

    if not current_user.backoffice_profile:
        raise ApiErrors({"global": ["utilisateur inconnu"]}, status_code=403)

    if not any(has_current_user_permission(permission) for permission in permissions):
        logger.warning(
            "user %s missed permission %s while trying to access %s",
            current_user.email,
            " or ".join(permission.name for permission in permissions),
            request.url,
        )

        raise ApiErrors({"global": ["permission manquante"]}, status_code=403)


def permission_required(permission: perm_models.Permissions) -> typing.Callable:
    """
    Ensure that the current user is connected and that it has the expected permission.
    """

    def wrapper(function: typing.Callable) -> typing.Callable:
        @wraps(function)
        def wrapped(*args: typing.Any, **kwargs: typing.Any) -> tuple[FlaskResponse, int] | typing.Callable:
            _check_any_permission_of((permission,))

            return function(*args, **kwargs)

        return wrapped

    return wrapper


def permission_required_in(permissions: typing.Iterable[perm_models.Permissions]) -> typing.Callable:
    """
    Ensure that the current user is connected and that it has one of the expected permissions.
    """

    def wrapper(function: typing.Callable) -> typing.Callable:
        @wraps(function)
        def wrapped(*args: typing.Any, **kwargs: typing.Any) -> tuple[FlaskResponse, int] | typing.Callable:
            _check_any_permission_of(permissions)

            return function(*args, **kwargs)

        return wrapped

    return wrapper


def custom_login_required(redirect_to: str) -> typing.Callable:
    def wrapper(function: typing.Callable) -> typing.Callable:
        @wraps(function)
        def wrapped(*args: typing.Any, **kwargs: typing.Any) -> tuple[FlaskResponse, int] | typing.Callable:
            if not current_user.is_authenticated:
                return redirect(url_for(redirect_to))

            return function(*args, **kwargs)

        return wrapped

    return wrapper
