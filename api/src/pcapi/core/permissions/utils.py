from functools import wraps
import logging
import typing

from flask import Response
from flask import request

from pcapi import settings
from pcapi.core.auth.api import BadPCToken
from pcapi.core.auth.api import ExpiredTokenError
from pcapi.core.auth.api import NotAPassCultureTeamAccountError
from pcapi.core.auth.api import authenticate_from_bearer
from pcapi.core.auth.utils import _set_current_permissions
from pcapi.core.auth.utils import _set_current_user
from pcapi.core.permissions.models import Permissions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.backoffice.blueprint import BACKOFFICE_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)


def permission_required(permission: Permissions) -> typing.Callable:
    def wrapper(func: typing.Callable) -> typing.Callable:
        add_security_scheme(func, BACKOFFICE_AUTH)

        @wraps(func)
        def wrapped(*args, **kwargs) -> typing.Union[tuple[Response, int], typing.Callable]:  # type: ignore[no-untyped-def]
            if not FeatureToggle.ENABLE_BACKOFFICE_API.is_active():
                raise ApiErrors(
                    {"global": "This function is behind the deactivated ENABLE_BACKOFFICE_API feature flag"},
                    status_code=403,
                )

            try:
                authorization = request.headers.get("Authorization", "")
                user, user_permissions = authenticate_from_bearer(authorization)
            except BadPCToken:
                raise ApiErrors({"global": "bad token"}, status_code=403)
            except ExpiredTokenError:
                raise ApiErrors({"global": "authentication expired"}, status_code=403)
            except NotAPassCultureTeamAccountError:
                raise ApiErrors({"global": "unknown user"}, status_code=403)

            _set_current_user(user)
            _set_current_permissions(user_permissions)

            if not settings.IS_TESTING:
                if permission.name not in user_permissions:
                    logger.warning(
                        "user %s missed permission %s while trying to access %s",
                        user.email,
                        permission.name,
                        request.url,
                    )
                    raise ApiErrors({"global": "missing permission"}, status_code=403)

            return func(*args, **kwargs)

        return wrapped

    return wrapper
