from functools import wraps
import logging
import typing

from flask import Response
from flask import jsonify
from flask import request

from pcapi import settings
from pcapi.core.auth.api import BadPCToken
from pcapi.core.auth.api import ExpiredTokenError
from pcapi.core.auth.api import NotAPassCultureTeamAccountError
from pcapi.core.auth.api import authenticate_from_bearer
from pcapi.core.permissions.models import Permissions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


def send_403(error_description: str) -> tuple[Response, int]:
    e = ApiErrors()
    e.add_error("global", error_description)
    return jsonify(e.errors), 403


def permission_required(permission: Permissions) -> typing.Callable:
    def wrapper(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def wrapped(*args, **kwargs) -> typing.Union[tuple[Response, int], typing.Callable]:  # type: ignore[no-untyped-def]
            if not FeatureToggle.ENABLE_BACKOFFICE_API.is_active():
                e = ApiErrors()
                e.add_error("global", "This function is behind the deactivated ENABLE_BACKOFFICE_API feature flag.")
                return jsonify(e.errors), 403

            if not settings.IS_TESTING:
                try:
                    authorization = request.headers.get("Authorization", "")
                    user, user_permissions = authenticate_from_bearer(authorization)
                except BadPCToken:
                    return send_403("bad token")
                except ExpiredTokenError:
                    return send_403("authentication expired")
                except NotAPassCultureTeamAccountError:
                    return send_403("unknown user")

                if permission.name not in user_permissions:
                    logger.warning(
                        "user %s missed permission %s while trying to access %s",
                        user.email,
                        permission.name,
                        request.url,
                    )
                    return send_403("missing permission")

            return func(*args, **kwargs)

        return wrapped

    return wrapper
