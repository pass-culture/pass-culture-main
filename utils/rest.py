""" rest """
import re
from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.functions import random 

from models.api_errors import ApiErrors
from models.db import db
from models.soft_deletable_mixin import SoftDeletableMixin
from sqlalchemy import text

from routes.serializer import as_dict
from utils.human_ids import dehumanize, humanize
from utils.string_processing import dashify


def get_provider_from_api_key():
    if 'apikey' in request.headers:
        Provider = Provider
        return Provider.query\
                       .filter_by(apiKey=request.headers['apikey'])\
                       .first()


def api_key_required(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        request.provider = get_provider_from_api_key()
        if request.provider is None:
            return "API key required", 403
        return f(*args, **kwds)
    return wrapper


def login_or_api_key_required(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        request.provider = get_provider_from_api_key()
        if request.provider is None:
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


def add_table_if_missing(sql_identifier, modelClass):
    if sql_identifier.find('.') == -1:
        return '"'+dashify(modelClass.__name__)+'".'+sql_identifier
    return sql_identifier


def query_with_order_by(query, order_by):
    if order_by:
        if type(order_by) == str:
            order_by = text(order_by)
        try:
            order_by = [order_by] if not isinstance(order_by, list)\
                       else order_by
            query = query.order_by(*order_by)
        except ProgrammingError as e:
            field = re.search('column "?(.*?)"? does not exist', e._message, re.IGNORECASE)
            if field:
                errors = ApiErrors()
                errors.add_error('order_by', 'order_by value references an unknown field : ' + field.group(1))
                raise errors
            else:
                raise e
    return query


def check_single_order_by_string(order_by_string):
    order_by_string = order_by_string.strip(' ')
    optional_table_prefix = '("?\\w+"?\\.|)'
    column_identifier = '"?\\w+"?'
    optional_sorting_order = '(|\\s+desc|\\s+asc)'
    if not re.match(f'^{optional_table_prefix}{column_identifier}{optional_sorting_order}$',
                    order_by_string,
                    re.IGNORECASE):
        api_errors = ApiErrors()
        api_errors.add_error('order_by',
                            'Invalid order_by field : "%s"' % order_by_string)
        raise api_errors


def order_by_is_native_sqlalchemy_clause(order_by):
    return isinstance(order_by, UnaryExpression) \
           or isinstance(order_by, InstrumentedAttribute) \
           or isinstance(order_by, random)


def check_order_by(order_by):
    if isinstance(order_by, list):
        for part in order_by:
            check_order_by(part)
    elif order_by_is_native_sqlalchemy_clause(order_by):
        pass
    elif isinstance(order_by, str):
        order_by = re.sub('coalesce\\((.*?)\\)',
                          '\\1',
                          order_by,
                          flags=re.IGNORECASE)
        for part in order_by.split(','):
            check_single_order_by_string(part)


def handle_rest_get_list(modelClass, query=None,
                         refine=None, order_by=None, flask_request=None,
                         include=None, resolve=None, print_elements=None,
                         paginate=None, page=None, populate=None):

    if flask_request is None:
        flask_request = request

    if query is None:
        query = modelClass.query

    # DELETED
    if issubclass(modelClass, SoftDeletableMixin):
        query = query.filter_by(isSoftDeleted=False)

    # REFINE
    if refine:
        query = refine(query)

    # ORDER BY
    if order_by:
        check_order_by(order_by)
        query = query_with_order_by(query, order_by)
    # PAGINATE
    if paginate:
        if page is not None:
            page = int(page)
        query = query.paginate(page, per_page=paginate, error_out=False)\
                     .items

    objects = [o for o in query]
    if populate:
        objects = list(map(populate, objects))

    # DICTIFY
    elements = [
        as_dict(o,
            include=include,
            resolve=resolve,
        ) for o in query
    ]

    # PRINT
    if print_elements:
        print(elements)

    # RETURN
    return jsonify(elements), 200


def ensure_provider_can_update(obj):
    if request.provider\
       and obj.lastProvider != request.provider:
        return "API key or login required", 403


def ensure_current_user_has_rights(rights, offerer_id, user=current_user):
    if not user.hasRights(rights, offerer_id):
        errors = ApiErrors()
        errors.add_error(
            'global',
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        )
        errors.status_code = 403
        raise errors


def feed(entity, json, keys):
    for key in keys:
        if key in json:
            entity.__setattr__(key, json[key])


def delete(entity):
    db.session.delete(entity)
    db.session.commit()
    return jsonify({"id": humanize(entity.id)}), 200


def load_or_404(obj_class, human_id):
    return obj_class.query.filter_by(id=dehumanize(human_id))\
                          .first_or_404()


def load_or_raise_error(obj_class, human_id):
    data = obj_class.query.filter_by(id=dehumanize(human_id)).first()
    if data is None:
        errors = ApiErrors()
        errors.add_error(
            'global',
            'Aucun objet ne correspond à cet identifiant dans notre base de données'
        )
        errors.status_code = 400
        raise errors
    else:
        return data
