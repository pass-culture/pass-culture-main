from functools import wraps
import logging
import random
import typing

from flask import Blueprint
from flask import Response as FlaskResponse
from flask import request
from flask import url_for
from flask_login import current_user
from flask_wtf import FlaskForm
import werkzeug
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import Forbidden
from werkzeug.wrappers import Response as WerkzeugResponse

from pcapi import settings
from pcapi.core.history import models as history_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.regions import get_all_regions

from . import blueprint


logger = logging.getLogger(__name__)


# perhaps one day we will be able to define it as str | tuple[str, int]
BackofficeResponse = typing.Union[str, typing.Tuple[str, int], WerkzeugResponse, Forbidden]


class UnauthenticatedUserError(Exception):
    pass


def has_current_user_permission(permission: perm_models.Permissions | str) -> bool:
    if isinstance(permission, str):
        permission = perm_models.Permissions[permission]
    return permission in current_user.backoffice_profile.permissions or settings.IS_TESTING


def _check_permission(permission: perm_models.Permissions) -> None:
    if not current_user.is_authenticated:
        raise UnauthenticatedUserError()

    if not current_user.backoffice_profile:
        raise ApiErrors({"global": ["utilisateur inconnu"]}, status_code=403)

    if not has_current_user_permission(permission):
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
        def wrapped(*args: typing.Any, **kwargs: typing.Any) -> tuple[FlaskResponse, int] | typing.Callable:
            _check_permission(permission)

            return func(*args, **kwargs)

        return wrapped

    return wrapper


def child_backoffice_blueprint(
    name: str, import_name: str, url_prefix: str, permission: perm_models.Permissions | None = None
) -> Blueprint:
    child_blueprint = Blueprint(name, import_name, url_prefix=url_prefix)
    blueprint.backoffice_v3_web.register_blueprint(child_blueprint)

    @child_blueprint.before_request
    def check_permission() -> None:
        if permission:
            _check_permission(permission)

    return child_blueprint


def custom_login_required(redirect_to: str) -> typing.Callable:
    def wrapper(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def wrapped(*args: typing.Any, **kwargs: typing.Any) -> tuple[FlaskResponse, int] | typing.Callable:
            if not current_user.is_authenticated:
                return werkzeug.utils.redirect(url_for(redirect_to))

            return func(*args, **kwargs)

        return wrapped

    return wrapper


def is_user_offerer_action_type(action: history_models.ActionHistory) -> bool:
    user_offerer_action_types = {
        history_models.ActionType.USER_OFFERER_NEW,
        history_models.ActionType.USER_OFFERER_PENDING,
        history_models.ActionType.USER_OFFERER_VALIDATED,
        history_models.ActionType.USER_OFFERER_REJECTED,
    }
    return action.actionType in user_offerer_action_types


def random_hash() -> str:
    return format(random.getrandbits(128), "x")


def format_ean_or_visa(ean: str) -> str:
    return ean.replace("-", "").replace(" ", "")


def is_ean_valid(ean: str) -> bool:
    ean = format_ean_or_visa(ean)
    return ean.isdigit() and len(ean) == 13


def is_visa_valid(visa: str) -> bool:
    visa = format_ean_or_visa(visa)
    return visa.isdigit() and len(visa) <= 10


def build_form_error_msg(form: FlaskForm) -> str:
    error_msg = "Les données envoyées comportent des erreurs."
    for field in form:
        if field.errors:
            error_msg += f" {field.label.text}: {', '.join(error for error in field.errors)};"

    return error_msg


def get_query_params() -> ImmutableMultiDict[str, str]:
    """
    Ignore empty query parameters so that they are considered as missing, not set to an empty string.
    This enables to fallback to the default value in wtforms field.
    request.args is an ImmutableMultiDict
    """
    return ImmutableMultiDict(item for item in request.args.items(multi=True) if item[1])


def is_feature_active(feature_name: str) -> bool:
    return feature.FeatureToggle[feature_name].is_active()


def get_setting(setting_name: str) -> typing.Any:
    return getattr(settings, setting_name)


def get_regions_choices() -> list[tuple]:
    return [(key, key) for key in get_all_regions()]
