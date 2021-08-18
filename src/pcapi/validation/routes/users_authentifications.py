from functools import wraps
import logging

from flask import _request_ctx_stack
from flask import g
from flask import request
from flask_login import current_user
from werkzeug.local import LocalProxy

from pcapi.core.offerers.api import find_api_key
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import repository as users_repo
from pcapi.core.users.models import User
from pcapi.models import ApiErrors
from pcapi.models.api_errors import UnauthorizedError
from pcapi.routes.pro.blueprints import API_KEY_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


logger = logging.getLogger(__name__)


def check_user_is_logged_in_or_email_is_provided(user: User, email: str):
    if not (user.is_authenticated or email):
        api_errors = ApiErrors()
        api_errors.add_error("email", "Vous devez préciser l'email de l'utilisateur quand vous n'êtes pas connecté(e)")
        raise api_errors


def login_or_api_key_required(function):
    @wraps(function)
    def wrapper(*args, **kwds):
        _fill_current_api_key()
        basic_authentication()

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


def basic_authentication(realm=None):
    auth = request.authorization
    # According to the Werkzeug documentation auth.password is None
    # for any auth that is not basic auth.
    if not auth or not auth.password:
        return None
    errors = UnauthorizedError(www_authenticate="Basic", realm=realm)
    try:
        user = users_repo.get_user_with_credentials(auth.username, auth.password)
    except users_exceptions.InvalidIdentifier as exc:
        errors.add_error("identifier", "Identifiant ou mot de passe incorrect")
        raise errors from exc
    except users_exceptions.UnvalidatedAccount as exc:
        errors.add_error("identifier", "Ce compte n'est pas validé.")
        raise errors from exc
    logger.info(
        "User logged in with authorization header",
        extra={"route": str(request.url_rule), "username": auth.username, "avoid_current_user": True},
    )
    # push the user to the current context - similar to flask-login
    ctx = _request_ctx_stack.top
    ctx.user = user
    return user
