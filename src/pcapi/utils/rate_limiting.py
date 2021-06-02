from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from pcapi import settings


def get_email_from_request() -> str:
    return request.json["identifier"]


rate_limiter = Limiter(
    strategy="fixed-window-elastic-expiry",
    key_func=get_remote_address,  # The default is a deprecated function that raises warning logs
)

ip_rate_limiter = rate_limiter.shared_limit(
    settings.RATE_LIMIT_BY_IP,
    key_func=get_remote_address,
    scope="ip_limiter",
    error_message="rate limit by ip exceeded",
)
email_rate_limiter = rate_limiter.shared_limit(
    settings.RATE_LIMIT_BY_EMAIL,
    key_func=get_email_from_request,
    scope="rate_limiter",
    error_message="rate limit by email exceeded",
)
