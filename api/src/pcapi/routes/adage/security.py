from functools import wraps

from flask import request

from pcapi import settings
from pcapi.models.api_errors import ForbiddenError


def adage_api_key_required(route_function):  # type: ignore [no-untyped-def]
    @wraps(route_function)
    def wrapper(*args, **kwds):  # type: ignore [no-untyped-def]
        mandatory_authorization_type = "Bearer "
        authorization_header = request.headers.get("Authorization")

        if authorization_header and mandatory_authorization_type in authorization_header:
            adage_api_key = authorization_header.replace(mandatory_authorization_type, "")
            if adage_api_key == settings.EAC_API_KEY:
                return route_function(*args, **kwds)

        raise ForbiddenError({"Authorization": ["Wrong api key"]})

    return wrapper
