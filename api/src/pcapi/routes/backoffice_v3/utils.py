from functools import wraps
import logging
import typing

from flask import Blueprint
from flask import Response as FlaskResponse
from flask import request
from flask import url_for
from flask_login import current_user
import werkzeug
from werkzeug.wrappers import Response as WerkzeugResponse

from pcapi import settings
from pcapi.core.permissions import models as perm_models
from pcapi.models.api_errors import ApiErrors

from . import blueprint


logger = logging.getLogger(__name__)


# perhaps one day we will be able to define it as str | tuple[str, int]
BackofficeResponse = typing.Union[str, typing.Tuple[str, int], WerkzeugResponse]


def _check_permission(permission: perm_models.Permissions) -> None:
    if not current_user.is_authenticated:
        raise ApiErrors({"global": ["l'utilisateur n'est pas authentifié"]}, status_code=403)

    if not current_user.backoffice_profile:
        raise ApiErrors({"global": ["utilisateur inconnu"]}, status_code=403)

    if permission not in current_user.backoffice_profile.permissions and not settings.IS_TESTING:
        logger.warning(
            "user %s missed permission %s while trying to access %s",
            current_user.email,
            permission.name,
            request.url,
        )

        raise ApiErrors({"global": ["permission manquante"]}, status_code=403)


def permission_required(permission: perm_models.Permissions) -> typing.Callable:
    """
    Ensure that the current user is connected and that it has the
    expected permissions.
    """

    def wrapper(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def wrapped(*args, **kwargs) -> tuple[FlaskResponse, int] | typing.Callable:  # type: ignore[no-untyped-def]
            _check_permission(permission)

            return func(*args, **kwargs)

        return wrapped

    return wrapper


def child_backoffice_blueprint(
    name: str, import_name: str, url_prefix: str, permission: perm_models.Permissions
) -> Blueprint:
    child_blueprint = Blueprint(name, import_name, url_prefix=url_prefix)
    blueprint.backoffice_v3_web.register_blueprint(child_blueprint)

    @child_blueprint.before_request
    def check_permission() -> None:
        _check_permission(permission)

    return child_blueprint


def custom_login_required(redirect_to: str) -> typing.Callable:
    def wrapper(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def wrapped(*args, **kwargs) -> tuple[FlaskResponse, int] | typing.Callable:  # type: ignore[no-untyped-def]
            if not current_user.is_authenticated:
                return werkzeug.utils.redirect(url_for(redirect_to))

            return func(*args, **kwargs)

        return wrapped

    return wrapper
