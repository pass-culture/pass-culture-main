""" rest """
from functools import wraps
import re

from flask import request
from flask_login import current_user
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.functions import random

from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import dehumanize


def login_or_api_key_required(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if not current_user.is_authenticated:
            return "API key or login required", 403

        return f(*args, **kwds)

    return wrapper


def expect_json_data(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if request.json is None:
            return "JSON data expected", 400
        return f(*args, **kwds)

    return wrapper


def check_single_order_by_string(order_by_string):
    order_by_string = order_by_string.strip(" ")
    optional_table_prefix = '("?\\w+"?\\.|)'
    column_identifier = '"?\\w+"?'
    optional_sorting_order = "(|\\s+desc|\\s+asc)"
    if not re.match(
        f"^{optional_table_prefix}{column_identifier}{optional_sorting_order}$", order_by_string, re.IGNORECASE
    ):
        api_errors = ApiErrors()
        api_errors.add_error("order_by", 'Invalid order_by field : "%s"' % order_by_string)
        raise api_errors


def order_by_is_native_sqlalchemy_clause(order_by):
    return isinstance(order_by, (UnaryExpression, InstrumentedAttribute, random))


def check_order_by(order_by):
    if isinstance(order_by, list):
        for part in order_by:
            check_order_by(part)
    elif order_by_is_native_sqlalchemy_clause(order_by):
        pass
    elif isinstance(order_by, str):
        order_by = re.sub("coalesce\\((.*?)\\)", "\\1", order_by, flags=re.IGNORECASE)
        for part in order_by.split(","):
            check_single_order_by_string(part)


def ensure_current_user_has_rights(rights, offerer_id, user=current_user):
    if not user.hasRights(rights, offerer_id):
        errors = ApiErrors()
        errors.add_error("global", "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information.")
        errors.status_code = 403
        raise errors


def load_or_404(obj_class, human_id):
    return obj_class.query.filter_by(id=dehumanize(human_id)).first_or_404()


def load_or_raise_error(obj_class, human_id):
    data = obj_class.query.filter_by(id=dehumanize(human_id)).first()
    if data is None:
        errors = ApiErrors()
        errors.add_error("global", "Aucun objet ne correspond à cet identifiant dans notre base de données")
        errors.status_code = 400
        raise errors
    else:
        return data
