from flask import request
from flask_login import current_user

from models import ApiErrors, User
from functools import wraps

from repository.api_key_queries import find_api_key_by_value


def check_user_is_logged_in_or_email_is_provided(user: User, email: str):
    if not (user.is_authenticated or email):
        api_errors = ApiErrors()
        api_errors.add_error('email',
                            'Vous devez préciser l\'email de l\'utilisateur quand vous n\'êtes pas connecté(e)')
        raise api_errors


def check_user_is_logged_in_or_api_key_is_provided(user: User, api_key: str):
    if not (user.is_authenticated or api_key):
        api_errors = ApiErrors()
        api_errors.add_error('api_key',
                            'Vous devez préciser l\'api key de l\'utilisateur quand vous n\'êtes pas connecté(e)')
        raise api_errors

def login_or_api_key_required_v2(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        authenticateUser = None
        authorization_header = request.headers.get('Authorization', None)

        if authorization_header:
            app_authorization_api_key = authorization_header.replace("Bearer ", "")
            authenticateUser = find_api_key_by_value(app_authorization_api_key)

        if authenticateUser is None:
            if not current_user.is_authenticated:
                return "API key or login required", 401
        return f(*args, **kwds)

    return wrapper
