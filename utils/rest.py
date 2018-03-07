from flask import jsonify, request, current_app as app
from flask_login import current_user
from functools import wraps
import re
from sqlalchemy.exc import ProgrammingError

from models.api_errors import ApiErrors
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


def update(obj, new_properties):
    print(new_properties)
    for (key, value) in new_properties.items():
        if key == 'id':
            continue
        setattr(obj, key, value)


def add_table_if_missing(sql_identifier, modelClass):
    if sql_identifier.find('.') == -1:
        return '"'+dashify(modelClass.__name__)+'".'+sql_identifier
    return sql_identifier


def handle_rest_get_list(modelClass, request, **options):
    # QUERY
    objects = modelClass.query
    # DELETED
    if hasattr(modelClass, 'deleted'):
        objects = objects.filter_by(deleted=False)
    # FILTER
    filters = request.args.copy()
    if 'filter_fn' in options:
        objects = options['filter_fn'](objects, filters)
    # ORDER BY
    if 'order_by' in options:
        try:
            if not isinstance(options['order_by'], list):
                order_by = [options['order_by']]
            else:
                order_by = options['order_by']
            objects = objects.order_by(*order_by)
        except ProgrammingError as e:
            field = re.search('column "?(.*?)"? does not exist', e._message, re.IGNORECASE)
            if field:
                errors = ApiErrors()
                errors.addError(field='order_by', errtype='unknown', error='order_by value references an unknown field : '+field.group(1))
                raise errors
            else:
                raise e
    # PAGINATE
    if 'paginate' in options:
        objects = objects.paginate(1, per_page=20, error_out=False)\
                         .items
    # DICTIFY
    elements = list(map(
        lambda o: o._asdict(
            include_joins='include_joins' in options and options['include_joins'],
            filters=filters
        ),
        objects))
    # PRINT
    if options.get('print_elements'):
        print(elements)
    # RETURN
    return jsonify(elements), 200

def get(modelClass, **options):
    # QUERY
    query = modelClass.query
    # DELETED
    if hasattr(modelClass, 'deleted'):
        query = query.filter_by(deleted=False)
    # FILTER
    if 'refine' in options:
        query = options['refine'](query)
    # DICTIFY
    include_joins = 'include_joins' in options and options['include_joins']
    elements = [obj._asdict(include_joins=include_joins) for obj in query]
    # PRINT
    if options.get('print_elements'):
        print(elements)
    # RETURN
    return jsonify(elements), 200

def ensure_provider_can_update(obj):
    if request.provider\
       and obj.lastProvider != request.provider:
        return "API key or login required", 403
