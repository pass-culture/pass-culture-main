from functools import wraps

from flask import request

from pcapi.models.api_errors import ForbiddenError
from pcapi.routes.eac.v1.blueprint import EAC_API_KEY_AUTH
from pcapi.serialization.spec_tree import add_security_scheme


def eac_api_key_required(route_function):
    add_security_scheme(route_function, EAC_API_KEY_AUTH)

    @wraps(route_function)
    def wrapper(*args, **kwds):
        mandatory_authorization_type = "Bearer "
        authorization_header = request.headers.get("Authorization")

        if authorization_header and mandatory_authorization_type in authorization_header:
            eac_api_key = authorization_header.replace(mandatory_authorization_type, "")
            if eac_api_key == "EAC_API_KEY":
                return route_function(*args, **kwds)

        raise ForbiddenError({"Authorization": ["Wrong api key"]})

    return wrapper
