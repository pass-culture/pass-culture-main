import random
import typing
from functools import wraps

from flask import Response as FlaskResponse
from flask import make_response

from pcapi import settings
from pcapi.models import feature


def random_hash() -> str:
    return format(random.getrandbits(128), "x")


def is_feature_active(feature_name: str) -> bool:
    return feature.FeatureToggle[feature_name].is_active()


def get_setting(setting_name: str) -> typing.Any:
    return getattr(settings, setting_name)


def no_cache() -> typing.Callable:
    def wrapper(function: typing.Callable) -> typing.Callable:
        @wraps(function)
        def wrapped(*args: typing.Any, **kwargs: typing.Any) -> tuple[FlaskResponse, int] | typing.Callable:
            response = make_response(function(*args, **kwargs))

            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

            return response

        return wrapped

    return wrapper
