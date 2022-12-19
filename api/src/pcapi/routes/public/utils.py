import base64
import binascii
import functools
import typing

import flask

from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers import repository as providers_repository


class InvalidBase64Exception(Exception):
    pass


def get_bytes_from_base64_string(base64_string: str) -> bytes:
    """Return the bytes from a base64 string."""
    try:
        return base64.b64decode(base64_string.encode("utf-8"))
    except binascii.Error as error:
        raise InvalidBase64Exception() from error


def individual_offers_api_provider(route_function: typing.Callable) -> typing.Callable:
    @functools.wraps(route_function)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:
        individual_offers_provider = providers_repository.get_provider_by_local_class(
            providers_constants.INDIVIDUAL_OFFERS_API_FAKE_CLASS_NAME
        )
        return route_function(individual_offers_provider=individual_offers_provider, *args, **kwargs)

    return wrapper
