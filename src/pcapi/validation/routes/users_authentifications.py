from functools import wraps

from flask import g
from flask import request
from flask_login import current_user
from werkzeug.local import LocalProxy

from pcapi.core.offerers.api import find_api_key
from pcapi.core.users.models import User
from pcapi.models import ApiErrors
from pcapi.routes.pro.blueprints import API_KEY_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


def check_user_is_logged_in_or_email_is_provided(user: User, email: str):
    if not (user.is_authenticated or email):
        api_errors = ApiErrors()
        api_errors.add_error("email", "Vous devez préciser l'email de l'utilisateur quand vous n'êtes pas connecté(e)")
        raise api_errors


def login_or_api_key_required(function):
    @wraps(function)
    def wrapper(*args, **kwds):
        _fill_current_api_key()

        if not g.current_api_key and not current_user.is_authenticated:
            return "API key or login required", 401
        return function(*args, **kwds)

    return wrapper


def api_key_required(route_function):
    add_security_scheme(route_function, API_KEY_AUTH)

    @wraps(route_function)
    def wrapper(*args, **kwds):
        _fill_current_api_key()

        if not g.current_api_key:
            return "API key required", 401
        return route_function(*args, **kwds)

    return wrapper


def _fill_current_api_key():
    mandatory_authorization_type = "Bearer "
    authorization_header = request.headers.get("Authorization")
    g.current_api_key = None

    if authorization_header and mandatory_authorization_type in authorization_header:
        app_authorization_credentials = authorization_header.replace(mandatory_authorization_type, "")
        g.current_api_key = find_api_key(app_authorization_credentials)


def _get_current_api_key():
    assert "current_api_key" in g, "Can only be used in a route wrapped with api_key_required"
    return g.current_api_key


current_api_key = LocalProxy(_get_current_api_key)
