from flask import request
from werkzeug.datastructures import ImmutableMultiDict


def get_query_params() -> ImmutableMultiDict[str, str]:
    """
    Ignore empty query parameters so that they are considered as missing, not set to an empty string.
    This enables to fallback to the default value in wtforms field.
    request.args is an ImmutableMultiDict
    """
    return ImmutableMultiDict(item for item in request.args.items(multi=True) if item[1])


def is_request_from_htmx() -> bool:
    return request.headers.get("hx-request") == "true" and not request.args.get("redirect", False)
