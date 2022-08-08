import typing

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from pcapi import settings


def get_email_from_request() -> str:
    return request.json["identifier"]  # type: ignore [index]


def get_basic_auth_from_request() -> str | None:
    # `pcapi.utis.login_manager` cannot be imported at module-scope,
    # because the application context may not be available and that
    # module needs it.
    from pcapi.utils.login_manager import get_request_authorization

    auth = get_request_authorization()
    if not auth or not auth.username:
        return None
    return auth.username


def get_username_or_remote_address() -> str:
    """Return username if authenticated, IP source address otherwise."""
    username = get_basic_auth_from_request()
    if username:
        return username
    return get_remote_address()


rate_limiter = Limiter(
    strategy="fixed-window-elastic-expiry",
    key_func=get_remote_address,  # The default is a deprecated function that raises warning logs
)


def ip_rate_limiter(**kwargs: typing.Any) -> typing.Callable:
    base_kwargs = {
        "key_func": get_remote_address,
        "scope": "ip_limiter",
        "error_message": "rate limit by ip exceeded",
    }
    base_kwargs.update(kwargs)
    return rate_limiter.shared_limit(settings.RATE_LIMIT_BY_IP, **base_kwargs)


def email_rate_limiter(**kwargs: typing.Any) -> typing.Callable:
    base_kwargs = {
        "key_func": get_email_from_request,
        "scope": "rate_limiter",
        "error_message": "rate limit by email exceeded",
    }
    base_kwargs.update(kwargs)
    return rate_limiter.shared_limit(settings.RATE_LIMIT_BY_EMAIL, **base_kwargs)


def basic_auth_rate_limiter(**kwargs: typing.Any) -> typing.Callable:
    base_kwargs = {
        "key_func": get_basic_auth_from_request,
        "exempt_when": lambda: get_basic_auth_from_request() is None,
        "deduct_when": lambda response: response.status_code == 401,
        "scope": "rate_limiter",
        "error_message": "rate limit by basic auth exceeded",
    }
    base_kwargs.update(kwargs)
    return rate_limiter.shared_limit(settings.RATE_LIMIT_BY_EMAIL, **base_kwargs)


def sirene_rate_limiter(**kwargs: typing.Any) -> typing.Callable:
    base_kwargs = {
        "key_func": get_username_or_remote_address,
        "scope": "rate_limiter",
        "error_message": "rate limit exceeded",
    }
    base_kwargs.update(kwargs)
    return rate_limiter.shared_limit(settings.RATE_LIMIT_SIRENE_API, **base_kwargs)
