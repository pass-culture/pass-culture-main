import logging
import os
import sys
import time

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask import Response
from flask import g
from flask import jsonify
from flask import request
from flask.logging import default_handler
import flask.wrappers
from flask_login import LoginManager
from flask_login import current_user
import prometheus_flask_exporter.multiprocess
import redis
import sentry_sdk
from sqlalchemy import orm
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix

from pcapi import settings
from pcapi.core import monkeypatches
from pcapi.core.finance import utils as finance_utils
from pcapi.core.logging import get_or_set_correlation_id
from pcapi.core.logging import install_logging
from pcapi.models import db
from pcapi.models import install_models
from pcapi.scripts.install import install_commands
from pcapi.utils.json_encoder import EnumJSONEncoder
from pcapi.utils.rate_limiting import rate_limiter
from pcapi.utils.sentry import init_sentry_sdk


monkeypatches.install_monkey_patches()

logger = logging.getLogger(__name__)

install_logging()

sentry_sdk.utils.MAX_STRING_LENGTH = 8192
init_sentry_sdk()


app = Flask(__name__, static_url_path="/static")


def setup_metrics(app_: Flask) -> None:
    if not int(os.environ.get("ENABLE_FLASK_PROMETHEUS_EXPORTER", "0")):
        return
    prometheus_flask_exporter.multiprocess.GunicornPrometheusMetrics(
        app_,
        group_by="url_rule",
    )
    # An external export server is started by Gunicorn, see `gunicorn.conf.py`.


# These `before_request()` and `after_request()` callbacks must be
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
def before_request() -> None:
    if current_user and current_user.is_authenticated:
        sentry_sdk.set_user(
            {
                "id": current_user.id,
            }
        )
    sentry_sdk.set_tag("correlation-id", get_or_set_correlation_id())
    g.request_start = time.perf_counter()


@app.after_request
def log_request_details(response: flask.wrappers.Response) -> flask.wrappers.Response:
    extra = {
        "statusCode": response.status_code,
        "method": request.method,
        "route": str(request.url_rule),  # e.g "/offers/<offer_id>"
        "path": request.path,
        "queryParams": request.query_string.decode(request.url_charset, errors="backslashreplace"),
        "size": response.headers.get("Content-Length", type=int),
        "deviceId": request.headers.get("device-id"),
        "sourceIp": request.headers.get("X-Forwarded-For", "").split(",", 1)[0] or None,  # ignore the proxy ips
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

    logger.info("HTTP request at %s", request.path, extra=extra)

    return response


@app.after_request
def add_security_headers(response: flask.wrappers.Response) -> flask.wrappers.Response:
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    return response


if not settings.IS_DEV or settings.IS_RUNNING_TESTS:
    # Remove default logger/handler, since we use our own (see pcapi.core.logging)
    app.logger.removeHandler(default_handler)

login_manager = LoginManager()

if settings.PROFILE_REQUESTS:
    profiling_restrictions = [settings.PROFILE_REQUESTS_LINES_LIMIT]
    app.config["PROFILE"] = True
    app.wsgi_app = ProfilerMiddleware(  # type: ignore [method-assign]
        app.wsgi_app,
        restrictions=profiling_restrictions,
    )

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)  # type: ignore [method-assign]

if not settings.JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not found in env")

app.secret_key = settings.FLASK_SECRET
app.json_encoder = EnumJSONEncoder

app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = settings.SQLALCHEMY_ECHO
app.config["RATELIMIT_STORAGE_URL"] = settings.REDIS_URL
app.config["GOOGLE_CLIENT_ID"] = settings.GOOGLE_CLIENT_ID
app.config["GOOGLE_CLIENT_SECRET"] = settings.GOOGLE_CLIENT_SECRET

rate_limiter.init_app(app)

install_models()
db.init_app(app)
orm.configure_mappers()
login_manager.init_app(app)
install_commands(app)
finance_utils.install_template_filters(app)

oauth = OAuth(app)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

app.url_map.strict_slashes = False


def generate_error_response(errors: dict, backoffice_template_name: str = "errors/generic.html") -> Response:
    return jsonify(errors)


with app.app_context():
    app.redis_client = redis.from_url(url=settings.REDIS_URL, decode_responses=True)  # type: ignore [attr-defined]
    app.generate_error_response = generate_error_response  # type: ignore [attr-defined]


@app.shell_context_processor
def get_shell_extra_context() -> dict:
    # We abuse `shell_context_processor` to call custom code when
    # `flask shell` is run.
    _set_python_prompt()
    return {}


@app.teardown_request
def remove_db_session(
    exc: BaseException | None = None,  # pylint: disable=unused-argument
) -> None:
    try:
        db.session.remove()
    except AttributeError:
        pass


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
