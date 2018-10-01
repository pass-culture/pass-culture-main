from flask import current_app as app
from flask import request

from validation.headers import check_header_validity

class InvalidHeader(Exception):
    pass

@app.before_request
def check_valid_header():
    header = request.headers.get('origin')
    endpoint = request.endpoint
    print('header', header)
    print('endpoint', endpoint)
    if not check_header_validity(header, endpoint):
        raise InvalidHeader