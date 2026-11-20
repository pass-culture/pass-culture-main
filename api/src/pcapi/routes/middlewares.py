import logging
import sys
import time

import flask.wrappers
import sentry_sdk
from flask import Response
from flask import current_app as app
from flask import g
from flask import request
from flask_login import current_user

from pcapi import settings
from pcapi.models import db
from pcapi.utils import transaction_manager
from pcapi.utils.logging import get_or_set_correlation_id
from pcapi.utils.sentry import SCRUBBED_INFO_PLACEHOLDER


logger = logging.getLogger(__name__)


def setup_atomic() -> None:
    """
    Must be before `setup_sentry_before_request` as it use the user and therefore call the db
    """
    if app.config.get("USE_GLOBAL_ATOMIC", False):
        transaction_manager._mark_session_as_managed()
        db.session.autoflush = False


# These `setup_sentry_before_request()` and `after_request()` callbacks must be
# registered first, so that:
# - our "before request" is called first to record the start time of
#   the request processing. If it was not the first callback, an
#   exception in another callback (such as RateLimitExceeded) would
#   prevent ours to be called;
# - our "log_request_details" is called last (sic) to, well, log.
#
# Reminder: functions registered for after request execution are
# called in reverse order of registration.
def setup_sentry_before_request() -> None:
    if current_user and current_user.is_authenticated:
        sentry_sdk.set_user(
            {
                "id": current_user.id,
            }
        )
    if device_id := request.headers.get("device-id", None):
        sentry_sdk.set_tag("device.id", device_id)
    sentry_sdk.set_tag("correlation-id", get_or_set_correlation_id())
    try:
        if (
            settings.BUG_BOUNTY_USER_AGENT
            and settings.BUG_BOUNTY_USER_AGENT.lower() in request.user_agent.string.lower()
        ):
            sentry_sdk.set_tag("is_bug_bounty", True)
    except RuntimeError:
        # not in a request, therefore it cannot be from a bug bounty user
        pass
    g.request_start = time.perf_counter()
    g.public_api_log_request_details_extra = {}


def log_request_details(response: flask.wrappers.Response) -> flask.wrappers.Response:
    is_sensitive_url_rule = request.url_rule and "/subscription/bonus" in str(request.url_rule)
    extra = {
        "statusCode": response.status_code,
        "method": request.method,
        "route": str(request.url_rule),  # e.g "/offers/<offer_id>"
        "path": request.path,
        "queryParams": request.query_string,
        "size": response.headers.get("Content-Length", type=int),
        "deviceId": SCRUBBED_INFO_PLACEHOLDER if is_sensitive_url_rule else request.headers.get("device-id"),
        "sourceIp": SCRUBBED_INFO_PLACEHOLDER if is_sensitive_url_rule else request.remote_addr,
        "requestId": request.headers.get("request-id"),
        "appVersion": request.headers.get("app-version"),
        "commitHash": request.headers.get("commit-hash"),
        "codePushId": request.headers.get("code-push-id"),
        "platform": request.headers.get("platform"),
    }
    try:
        duration = round((time.perf_counter() - g.request_start) * 1000)  # milliseconds
    except AttributeError:
        # If an error occurs in any "before request" function before
        # our `before_request()` above is called, `g.request_start`
        # will not be set. It is unlikely since our callback should be
        # the first, but it warrants an analysis.
        logger.warning("g.request_start was not available in log_request_details", exc_info=True)
    else:
        extra["duration"] = duration

    try:
        extra.update(g.public_api_log_request_details_extra)
    except AttributeError:
        logger.warning("g.public_api_log_request_details_extra was not available in log_request_details", exc_info=True)
    except Exception:
        logger.warning("g.public_api_log_request_details_extra does not seem to contain a valid dict", exc_info=True)

    logger.info("HTTP request at %s", request.path, extra=extra)

    return response


def add_security_headers(response: flask.wrappers.Response) -> flask.wrappers.Response:
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    return response


def mark_4xx_as_invalid(response: flask.Response) -> flask.Response:
    if app.config.get("USE_GLOBAL_ATOMIC", False) and response.status_code >= 400:
        transaction_manager.mark_transaction_as_invalid()
    return response


def remove_db_session(exc: BaseException | None = None) -> None:
    try:
        db.session.remove()
    except Exception as exception:
        logger.exception(
            "An error happened while removing the transaction",
            extra={
                "exc": str(exception),
            },
        )


def teardown_atomic(exc: BaseException | None = None) -> None:
    if app.config.get("USE_GLOBAL_ATOMIC", False):
        try:
            if exc:
                transaction_manager.mark_transaction_as_invalid()
            transaction_manager._finalize_managed_session()
            db.session.autoflush = True
        except Exception as exception:
            logger.exception(
                "An error happened while managing the transaction",
                extra={
                    "exc": str(exception),
                },
            )


def get_shell_extra_context() -> dict:
    # We abuse `shell_context_processor` to call custom code when
    # `flask shell` is run.
    def _non_printable(seq: str) -> str:
        return f"\001{seq}\002"

    env = settings.ENV
    if env in "production":
        color = "\x1b[1;49;31m"  # red
    elif env == "staging":
        color = "\x1b[1;49;35m"  # purple
    elif env == "testing":
        color = "\x1b[1;49;36m"  # cyan
    else:
        color = None

    if color:
        color = _non_printable(color)
        reset = _non_printable("\x1b[0m")

        sys.ps1 = f"{color}{env} >>> {reset}"

    return {}


def add_headers(response: Response) -> Response:
    # Cache static files in the browser to avoid many requests when every page is loaded, which would cause many
    # database queries for users in before_request() and many logs printed (on 2024-10-09, 36 files, 72 db queries).
    if request.path.startswith("/static/") or request.path.startswith("/favicon"):
        response.headers["Cache-Control"] = "public,max-age=3600"

    return response
