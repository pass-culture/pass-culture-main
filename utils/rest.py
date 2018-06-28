from functools import wraps
import re
from flask import abort, jsonify, request, current_app as app
from flask_login import current_user
from sqlalchemy.exc import ProgrammingError

from models.api_errors import ApiErrors
from utils.human_ids import dehumanize, humanize
from utils.string_processing import dashify


def get_provider_from_api_key():
    if 'apikey' in request.headers:
        Provider = app.model.Provider
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


def update(obj, new_properties, **kwargs):
    skipped_keys = kwargs.get('skipped_keys', [])
    for (key, value) in new_properties.items():
        if key in skipped_keys:
            continue
        elif key == 'id':
            continue
        elif key == 'validationToken':
            continue
        elif key.endswith('Id'):
            setattr(obj, key, dehumanize(value))
        else:
            setattr(obj, key, value)


def add_table_if_missing(sql_identifier, modelClass):
    if sql_identifier.find('.') == -1:
        return '"'+dashify(modelClass.__name__)+'".'+sql_identifier
    return sql_identifier


def handle_rest_get_list(modelClass, query=None,
                         refine=None, order_by=None, flask_request=None,
                         include=None, resolve=None, print_elements=None,
                         paginate=None, page=None):
    if flask_request is None:
        flask_request = request
    if query is None:
        query = modelClass.query
    # DELETED
    if hasattr(modelClass, 'deleted'):
        query = query.filter_by(deleted=False)
    # REFINE
    if refine:
        query = refine(query)
    # ORDER BY
    if order_by:
        try:
            order_by = [order_by] if not isinstance(order_by, list)\
                       else order_by
            query = query.order_by(*order_by)
        except ProgrammingError as e:
            field = re.search('column "?(.*?)"? does not exist', e._message, re.IGNORECASE)
            if field:
                errors = ApiErrors()
                errors.addError('order_by', 'order_by value references an unknown field : '+field.group(1))
                raise errors
            else:
                raise e
    # PAGINATE
    if paginate:
        if page is not None:
            page = int(page)
        query = query.paginate(page, per_page=paginate, error_out=False)\
                     .items
    # DICTIFY
    elements = list(map(
        lambda o: o._asdict(
            include=include,
            resolve=resolve,
        ),
        query))
    # PRINT
    if print_elements:
        print(elements)
    # RETURN
    return jsonify(elements), 200


def ensure_provider_can_update(obj):
    if request.provider\
       and obj.lastProvider != request.provider:
        return "API key or login required", 403


def ensure_current_user_has_rights(rights, offererId):
    if not current_user.hasRights(rights, offererId):
        abort(403)

def ensure_can_be_updated(model, id):
    element = load_or_404(model, id)
    if element.lastProvider:
        errors = ApiErrors()
        errors.addError(
            'global',
            'not allowed because data come from provider ' + element.lastProvider.name
        )
        raise errors
    return element

def feed(entity, json, keys):
    for key in keys:
        if key in json:
            entity.__setattr__(key, json[key])


def delete(entity):
    app.db.session.delete(entity)
    app.db.session.commit()
    return jsonify({"id": humanize(entity.id)}), 200


def load_or_404(obj_class, human_id):
    return obj_class.query.filter_by(id=dehumanize(human_id))\
                          .first_or_404()
