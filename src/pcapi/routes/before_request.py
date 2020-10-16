from flask import current_app as app
from flask import request


class InvalidOriginHeader(Exception):
    pass


# @app.before_request
# def check_valid_origin_header():
#     header = request.headers.get('origin')
#     endpoint = request.endpoint
#
#     if not check_origin_header_validity(header, endpoint, request.path):
#         raise InvalidOriginHeader
