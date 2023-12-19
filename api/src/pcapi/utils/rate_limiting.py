import typing

import flask
from flask import g
from flask import request
import flask_limiter
from flask_limiter.util import get_remote_address

from pcapi import settings
from pcapi.models.feature import FeatureToggle


def get_email_from_request() -> str:
    return request.json["identifier"]  # type: ignore [index]


def get_api_key() -> str:
    return g.current_api_key


def get_basic_auth_from_request() -> str:
    # `pcapi.utis.login_manager` cannot be imported at module-scope,
    # because the application context may not be available and that
    # module needs it.
    from pcapi.utils.login_manager import get_request_authorization

    auth = get_request_authorization()
    if not auth or not auth.username:
        return ""
    return auth.username


def get_username_or_remote_address() -> str:
    """Return username if authenticated, IP source address otherwise."""
    username = get_basic_auth_from_request()
    if username:
        return username
    return get_remote_address()


class Limiter(flask_limiter.Limiter):
    """A custom class that can completely disable rate-limiting if a
    feature flag is enabled.
    """

    def _check_request_limit(
        self,
        callable_name: str | None = None,
        in_middleware: bool = True,
    ) -> None:
        if not settings.IS_RUNNING_TESTS and not FeatureToggle.WIP_ENABLE_RATE_LIMITING.is_active():
            return None
        return super()._check_request_limit(
            callable_name=callable_name,
            in_middleware=in_middleware,
        )


rate_limiter = Limiter(
    storage_uri=settings.REDIS_URL,
    strategy="fixed-window-elastic-expiry",
    key_func=get_remote_address,  # The default is a deprecated function that raises warning logs
)


def ip_rate_limiter(
    deduct_when: typing.Callable[[flask.wrappers.Response], bool] | None = None,
) -> typing.Callable:
    return rate_limiter.shared_limit(
        settings.RATE_LIMIT_BY_IP,
        scope="ip_limiter",
        key_func=get_remote_address,
        error_message="rate limit by ip exceeded",
        deduct_when=deduct_when,
    )


def email_rate_limiter() -> typing.Callable:
    return rate_limiter.shared_limit(
        settings.RATE_LIMIT_BY_EMAIL,
        scope="rate_limiter",
        key_func=get_email_from_request,
        exempt_when=lambda: not get_email_from_request(),
        error_message="rate limit by email exceeded",
    )


def api_key_high_rate_limiter() -> typing.Callable:
    return _api_key_rate_limiter(settings.HIGH_RATE_LIMIT_BY_API_KEY)


def api_key_low_rate_limiter() -> typing.Callable:
    return _api_key_rate_limiter(settings.LOW_RATE_LIMIT_BY_API_KEY)


def _api_key_rate_limiter(rate_limit: str) -> typing.Callable:
    return rate_limiter.shared_limit(
        rate_limit,
        scope="rate_limiter",
        key_func=get_api_key,
        error_message="rate limit by api_key exceeded",
    )


def basic_auth_rate_limiter() -> typing.Callable:
    return rate_limiter.shared_limit(
        settings.RATE_LIMIT_BY_EMAIL,
        scope="rate_limiter",
        key_func=get_basic_auth_from_request,
        exempt_when=lambda: not get_basic_auth_from_request(),
        deduct_when=lambda response: response.status_code == 401,
        error_message="rate limit by basic auth exceeded",
    )


def sirene_rate_limiter() -> typing.Callable:
    return rate_limiter.shared_limit(
        settings.RATE_LIMIT_SIRENE_API,
        scope="rate_limiter",
        key_func=get_username_or_remote_address,
        error_message="rate limit exceeded",
    )
