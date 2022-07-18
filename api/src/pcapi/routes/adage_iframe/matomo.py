"""
    experimental module to integrate matomo tracking in passculture api
"""
import functools
import hashlib
import typing

from pcapi.models.feature import FeatureToggle
from pcapi.utils import requests


def matomo(**kwargs) -> typing.Callable:  # type: ignore [no-untyped-def]
    def decorator(function: typing.Callable) -> typing.Callable:
        @functools.wraps(function)
        def wrapper(*args, **kwargs) -> typing.Callable:  # type: ignore [no-untyped-def]
            if FeatureToggle.ENABLE_MATOMO_TRACKING_ADAGE_IFRAME_TEST.is_active():
                if "authenticated_information" in kwargs:
                    email = kwargs["authenticated_information"].email.encode("utf-8")
                    email_hash = hashlib.sha256(email).hexdigest()
                    tracking = {
                        "idsite": 1,
                        "rec": 1,  # mandatory useless arg
                        "action_name": function.__name__,
                        "_id": email_hash[:16],
                    }
                    url = "https://passculturetesting.matomo.cloud/matomo.php"
                    try:
                        requests.get(url, params=tracking)
                    except Exception:  # pylint: disable=broad-except
                        pass  # it's a poc we don't care about errors
            return function(*args, **kwargs)

        return wrapper

    return decorator
