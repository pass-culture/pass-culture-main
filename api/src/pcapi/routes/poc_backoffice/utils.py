from functools import wraps
import logging
import typing

from flask import Response
from flask import request
from flask import url_for
from flask_login import current_user
import werkzeug

from pcapi import settings
from pcapi.core.permissions.models import Permissions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


def ff_enabled(feature: FeatureToggle, redirect_to: str | None) -> typing.Callable:
    def wrapper(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def wrapped(*args, **kwargs) -> tuple[Response, int] | typing.Callable:  # type: ignore[no-untyped-def]
            if not feature.is_active():
                if redirect_to:
                    return werkzeug.utils.redirect(url_for(redirect_to))

                raise ApiErrors(
                    {"global": f"This function is behind the deactivated {feature.name} feature flag"},
                    status_code=403,
                )

            return func(*args, **kwargs)

        return wrapped

    return wrapper


def permission_required(permission: Permissions, redirect_to: str | None) -> typing.Callable:
    def wrapper(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def wrapped(*args, **kwargs) -> tuple[Response, int] | typing.Callable:  # type: ignore[no-untyped-def]
            user_permission_names = {perm.name for perm in current_user.backoffice_permissions}
            if permission.name not in user_permission_names and not settings.IS_TESTING:
                logger.warning(
                    "user %s missed permission %s while trying to access %s",
                    current_user.email,
                    permission.name,
                    request.url,
                )

                if redirect_to:
                    return werkzeug.utils.redirect(url_for(redirect_to))

                raise ApiErrors({"global": "missing permission"}, status_code=403)

            return func(*args, **kwargs)

        return wrapped

    return wrapper


def custom_login_required(redirect_to: str) -> typing.Callable:
    def wrapper(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def wrapped(*args, **kwargs) -> tuple[Response, int] | typing.Callable:  # type: ignore[no-untyped-def]
            if not current_user.is_authenticated:
                return werkzeug.utils.redirect(url_for(redirect_to))

            return func(*args, **kwargs)

        return wrapped

    return wrapper
