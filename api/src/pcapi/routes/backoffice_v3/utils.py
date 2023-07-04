from functools import wraps
import logging
import operator as op
import random
import typing

from flask import Blueprint
from flask import Response as FlaskResponse
from flask import request
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
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

OPERATOR_DICT = {
    "EQUALS": op.eq,
    "NOT_EQUALS": op.ne,
    "GREATER_THAN": op.gt,
    "GREATER_THAN_OR_EQUAL_TO": op.ge,
    "LESS_THAN": op.lt,
    "LESS_THAN_OR_EQUAL_TO": op.le,
    "IN": lambda x, y: x.in_(y),
    "NOT_IN": lambda x, y: x.not_in(y),
    "CONTAINS": lambda x, y: x.ilike(f"%{y}%"),
    "NO_CONTAINS": lambda x, y: ~x.ilike(f"%{y}%"),
}


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
            for error in field.errors:
                field_errors = []
                # form field errors are a dict, where keys are the failing field's name, and
                # the value is a list of all error messages
                if isinstance(error, dict):
                    field_errors += [
                        ", ".join(error_text for error_text in field_error_list) for field_error_list in error.values()
                    ]
                else:
                    field_errors.append(error)
            error_msg += f" {field.label.text}: {', '.join(error for error in field_errors)};"
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


def generate_search_query(
    query: BaseQuery,
    *,
    search_parameters: typing.Iterable[dict[str, typing.Any]],
    fields_definition: dict[str, dict[str, typing.Any]],
    joins_definition: dict[str, list[tuple[str, tuple]]],
    operators_definition: dict | None = None,
) -> tuple[BaseQuery, set[str], set[str]]:
    """
    Generate a search query from a list of dict (from a ListField of FormFields).

    query: the query object to use
    search_parameters: list of dict representing the user's query. each dict must have at least the fields:
        - operator: a key for operators_definition
        - search_field: a key for fields_definition
    fields_definition: a dict defining the fields, joins and special operations
    joins_definition: a dict defining how to do each join
    operators_definition: a dict mapping str to actual operations
    """
    operators_definition = operators_definition or OPERATOR_DICT
    joins: set[tuple] = set()
    filters: list = []
    warnings: set[str] = set()
    for search_data in search_parameters:
        operator = search_data.get("operator", "")
        if operator not in operators_definition:
            continue

        search_field = search_data.get("search_field")
        if not search_field:
            continue

        if search_field not in fields_definition:
            warnings.add(f"La règle de recherche '{search_field}' n'est pas supportée, merci de prévenir les devs")
            continue

        meta_field = fields_definition.get(search_field)
        if not meta_field:
            warnings.add(f"La règle de recherche '{search_field}' n'est pas supportée, merci de prévenir les devs")
            continue
        field_value = meta_field.get("special", lambda x: x)(search_data.get(meta_field["field"]))
        column = meta_field["column"]
        if "join" in meta_field:
            joins.add(meta_field["join"])
        filters.append(operators_definition[operator](column, field_value))

    query, join_log = _manage_joins(query=query, joins=joins, joins_definition=joins_definition)
    if filters:
        query = query.filter(*filters)
    return query, join_log, warnings


def _manage_joins(
    query: BaseQuery, joins: set, joins_definition: dict[str, list[tuple[str, tuple]]]
) -> tuple[BaseQuery, set[str]]:
    join_log = set()
    join_containers = sorted((joins_definition[join] for join in joins), key=len, reverse=True)
    for join_continer in join_containers:
        for join_tuple in join_continer:
            join_name, *join_args = join_tuple
            if not join_name in join_log:
                query = query.join(*join_args)
                join_log.add(join_name)
    return query, join_log
