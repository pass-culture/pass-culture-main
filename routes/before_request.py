from functools import wraps

from flask import current_app as app
from flask import request

from validation.headers import get_header_whitelist

header_whitelist = get_header_whitelist()


@app.before_request
def check_valid_header():
    header = request.headers.get('origin')
    if not header in header_whitelist:
        return


def validate_any_header(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        header = request.headers.get('origin')
        header_whitelist.append(header)
        return f(*args, **kwargs)

    return decorated_function
