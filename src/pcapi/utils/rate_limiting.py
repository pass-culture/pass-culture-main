from typing import Callable
from typing import Optional

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from pcapi import settings


def get_email_from_request() -> str:
    return request.json["identifier"]


def get_basic_auth_from_request() -> Optional[str]:
    auth = request.authorization
    if not auth or not auth.username:
        return None
    return auth.username


rate_limiter = Limiter(
    strategy="fixed-window-elastic-expiry",
    key_func=get_remote_address,  # The default is a deprecated function that raises warning logs
)


def ip_rate_limiter(**kwargs) -> Callable:
    base_kwargs = {
        "key_func": get_remote_address,
        "scope": "ip_limiter",
        "error_message": "rate limit by ip exceeded",
    }
    base_kwargs.update(kwargs)
    return rate_limiter.shared_limit(settings.RATE_LIMIT_BY_IP, **base_kwargs)


def email_rate_limiter(**kwargs) -> Callable:
    base_kwargs = {
        "key_func": get_email_from_request,
        "scope": "rate_limiter",
        "error_message": "rate limit by email exceeded",
    }
    base_kwargs.update(kwargs)
    return rate_limiter.shared_limit(settings.RATE_LIMIT_BY_EMAIL, **base_kwargs)
