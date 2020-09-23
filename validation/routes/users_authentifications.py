from functools import wraps

from flask import request
from flask_login import current_user

from models import ApiErrors, UserSQLEntity
from repository.api_key_queries import find_api_key_by_value


def check_user_is_logged_in_or_email_is_provided(user: UserSQLEntity, email: str):
    if not (user.is_authenticated or email):
        api_errors = ApiErrors()
        api_errors.add_error('email', "Vous devez préciser l'email de l'utilisateur quand vous n'êtes pas connecté(e)")
        raise api_errors


def login_or_api_key_required_v2(function):
    @wraps(function)
    def wrapper(*args, **kwds):
        mandatory_authorization_type = 'Bearer '
        is_valid_api_key = False
        authorization_header = request.headers.get('Authorization')

        if authorization_header and mandatory_authorization_type in authorization_header:
            app_authorization_credentials = authorization_header.replace(mandatory_authorization_type, '')
            is_valid_api_key = bool(find_api_key_by_value(app_authorization_credentials))

        if not is_valid_api_key and not current_user.is_authenticated:
            return 'API key or login required', 401
        return function(*args, **kwds)

    return wrapper
