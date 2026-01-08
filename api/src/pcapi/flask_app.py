import logging
import os
import sys
import time
import typing

import flask.wrappers
import prometheus_flask_exporter.multiprocess
import redis
import sentry_sdk
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask import Response
from flask import g
from flask import jsonify
from flask import request
from flask.logging import default_handler
from flask_login import current_user
from sqlalchemy.event import listens_for
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix

from pcapi import settings
from pcapi.celery_tasks.celery import celery_init_app
from pcapi.celery_tasks.config import CELERY_BASE_SETTINGS
from pcapi.core import monkeypatches
from pcapi.core.finance import utils as finance_utils
from pcapi.core.logging import get_or_set_correlation_id
from pcapi.core.logging import install_logging
from pcapi.models import db
from pcapi.models import install_models
from pcapi.scripts.install import install_commands
from pcapi.utils import transaction_manager
from pcapi.utils.json_encoder import EnumJSONEncoder
from pcapi.utils.sentry import init_sentry_sdk


URL_PREFIX_VALUES = [
    "account-update-requests",
    "backoffice",
    "individual-bookings",
    "openapi.json",
    "account-update-requests",
    "adage",
    "adage-iframe",
    "auth",
    "health",
    "individual-bookings",
    "institutional",
    "native",
    "pro",
    "public",
    "public-accounts",
    "webhooks",
]

monkeypatches.install_monkey_patches()

logger = logging.getLogger(__name__)

install_logging()

init_sentry_sdk()


app = Flask(__name__, static_url_path="/static")


def setup_metrics(app_: Flask) -> None:
    if not int(os.environ.get("ENABLE_FLASK_PROMETHEUS_EXPORTER", "0")):
        return

    def get_top_level_blueprint_name() -> str | None:
        if hasattr(request, "blueprint") and request.blueprint is not None:
            blueprint_list = request.blueprint.split(".")
            if blueprint_list and blueprint_list[0] is not None:
                return blueprint_list[0]
        return "other"

    def get_url_prefix() -> str | None:
        path = request.path
        # Request.path always includes a leading slash
        prefix = next((p for p in path.split("/") if p), None)
        if prefix not in URL_PREFIX_VALUES:
            return "other"
        return prefix

    prometheus_flask_exporter.multiprocess.GunicornPrometheusMetrics(
        app_,
        group_by="url_rule",
        default_labels={"url_prefix": get_url_prefix, "route_blueprint": get_top_level_blueprint_name},
    )
    # An external export server is started by Gunicorn, see `gunicorn.conf.py`.


@app.before_request
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
@app.before_request
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
    g.request_start = time.perf_counter()
    g.public_api_log_request_details_extra = {}


@app.after_request
def log_request_details(response: flask.wrappers.Response) -> flask.wrappers.Response:
    extra = {
        "statusCode": response.status_code,
        "method": request.method,
        "route": str(request.url_rule),  # e.g "/offers/<offer_id>"
        "path": request.path,
        "queryParams": request.query_string,
        "size": response.headers.get("Content-Length", type=int),
        "deviceId": request.headers.get("device-id"),
        "sourceIp": request.remote_addr,
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


@app.after_request
def add_security_headers(response: flask.wrappers.Response) -> flask.wrappers.Response:
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    return response


if settings.REMOVE_LOGGER_HANDLER:
    # Remove default logger/handler, since we use our own (see pcapi.core.logging)
    app.logger.removeHandler(default_handler)


if settings.PROFILE_REQUESTS:
    profiling_restrictions = [settings.PROFILE_REQUESTS_LINES_LIMIT]
    app.config["PROFILE"] = True
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app,
        restrictions=profiling_restrictions,
    )


# Our L7 load balancer adds 2 IPs to the `X-Forwarded-For` HTTP header.
# And there is another proxy in front of our app. Hence `x_for=3`.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=3)

if not settings.JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not found in env")

app.secret_key = settings.FLASK_SECRET
app.json_provider_class = EnumJSONEncoder
app.json = EnumJSONEncoder(app)

app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = settings.SQLALCHEMY_ECHO
app.config["GOOGLE_CLIENT_ID"] = settings.GOOGLE_CLIENT_ID  # for authlib
app.config["GOOGLE_CLIENT_SECRET"] = settings.GOOGLE_CLIENT_SECRET  # for authlib

install_models()

db.init_app(app)

sa_orm.configure_mappers()
install_commands(app)
finance_utils.install_template_filters(app)

app.config.from_mapping(
    CELERY=CELERY_BASE_SETTINGS,
)

celery_init_app(app)


backoffice_oauth = OAuth(app)
backoffice_oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

native_app_oauth = OAuth(app)
native_app_oauth.register(
    name="google",
    client_id=settings.NATIVE_APP_GOOGLE_CLIENT_ID,
    client_secret=settings.NATIVE_APP_GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


app.url_map.strict_slashes = False


# The argument `backoffice_template_name` is not used, but it is needed
# to have the same signature as `backoffice_app.generate_error_response()`.
def generate_error_response(errors: dict, backoffice_template_name: str = "not used") -> Response:
    return jsonify(errors)


with app.app_context():
    app.redis_client = redis.from_url(url=settings.REDIS_URL, decode_responses=True)
    app.generate_error_response = generate_error_response


@app.shell_context_processor
def get_shell_extra_context() -> dict:
    # We abuse `shell_context_processor` to call custom code when
    # `flask shell` is run.
    _set_python_prompt()
    return {}


@app.after_request
def mark_4xx_as_invalid(response: flask.Response) -> flask.Response:
    if app.config.get("USE_GLOBAL_ATOMIC", False):
        if response.status_code >= 400:
            transaction_manager.mark_transaction_as_invalid()
    return response


@app.teardown_request
def remove_db_session(exc: BaseException | None = None) -> None:
    try:
        db.session.remove()
    except Exception as exception:
        logger.error(
            "An error happened while removing the transaction",
            extra={
                "exc": str(exception),
            },
            exc_info=True,
        )


@app.teardown_request
def teardown_atomic(exc: BaseException | None = None) -> None:
    if app.config.get("USE_GLOBAL_ATOMIC", False):
        try:
            if exc:
                transaction_manager.mark_transaction_as_invalid()
            transaction_manager._finalize_managed_session()
            db.session.autoflush = True
        except Exception as exception:
            logger.error(
                "An error happened while managing the transaction",
                extra={
                    "exc": str(exception),
                },
                exc_info=True,
            )


with app.app_context():
    # Invalidates connections that are being shared accross process boundaries
    # see https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
    @sa.event.listens_for(db.engine, "connect")
    def connect(dbapi_connection: typing.Any, connection_record: typing.Any) -> None:
        connection_record.info["pid"] = os.getpid()

    @sa.event.listens_for(db.engine, "checkout")
    def checkout(dbapi_connection: typing.Any, connection_record: typing.Any, connection_proxy: typing.Any) -> None:
        pid = os.getpid()
        if connection_record.info["pid"] != pid:
            connection_record.connection = connection_proxy.connection = None
            raise sa.exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" % (connection_record.info["pid"], pid)
            )


def _non_printable(seq: str) -> str:
    return f"\001{seq}\002"


def _set_python_prompt() -> None:
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


# Install soft deletion hook if enabled
if settings.SOFTDELETE_ENABLED:

    @listens_for(sa_orm.Session, identifier="do_orm_execute")
    def soft_delete_execute(state: sa_orm.ORMExecuteState) -> None:
        import sqlalchemy_easy_softdelete.handler.rewriter as softdelete_rewriter

        # TODO: check with UPDATE and SELECT in subquery. Does it still work ?
        if not state.is_select:
            return

        # Rewrite the statement
        global_rewriter = softdelete_rewriter.SoftDeleteQueryRewriter(
            deleted_field_name="isSoftDeleted",
            disable_soft_delete_option_name="include_deleted",
            enabled_tables=[softdelete_rewriter.EnabledTable("venue", None)],
        )
        adapted = global_rewriter.rewrite_statement(state.statement)

        # Replace the statement
        state.statement = adapted
