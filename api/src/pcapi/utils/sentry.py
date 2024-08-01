import random
import sys
import typing

from pydantic.v1 import ValidationError
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from pcapi import settings
from pcapi.routes import UrlPrefix
import pcapi.routes.apis as routes_apis
import pcapi.routes.backoffice.blueprint as backoffice_blueprint
import pcapi.routes.pro.blueprint as pro_blueprint
import pcapi.routes.public.blueprints as public_api_blueprints
import pcapi.tasks.decorator as tasks_decorator
from pcapi.utils.health_checker import read_version_from_file


if typing.TYPE_CHECKING:
    from sentry_sdk.types import Event


DEFAULT_SAMPLE_RATE = settings.SENTRY_DEFAULT_TRACES_SAMPLE_RATE
LOW_SAMPLE_RATE = DEFAULT_SAMPLE_RATE / 10
LOWER_SAMPLE_RATE = DEFAULT_SAMPLE_RATE / 100
LOWEST_SAMPLE_RATE = DEFAULT_SAMPLE_RATE / 1000
NO_SAMPLE_RATE = 0.0


def before_send(event: "Event", _hint: dict[str, typing.Any]) -> "Event | None":
    if _is_flask_shell_event():
        return None

    if custom_fingerprint := get_custom_fingerprint(_hint):
        event["fingerprint"] = ["{{ default }}", custom_fingerprint]
    return event


def traces_sampler(sampling_context: dict) -> float:
    """
    This sampler defines a fraction of the DEFAULT_SAMPLE_RATE according to the requested path
    The sentry SDK will then apply that rate to decide if the transaction should be sampled
    At this time, the transaction name has not yet been defined by Flask, but we will later filter out
    some events in before_send_transaction()
    """
    path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO")

    match path:
        # monitoring endpoints
        case "/health/api":
            score = NO_SAMPLE_RATE
        case "/health/database":
            score = NO_SAMPLE_RATE

        # high volume paths
        case "/users/current":
            score = LOWEST_SAMPLE_RATE
        case "/features":
            score = LOWEST_SAMPLE_RATE
        case _ if path.startswith("/.well-knwon/"):
            score = LOWEST_SAMPLE_RATE

        # static files for BO
        case _ if path.startswith("/static"):
            score = NO_SAMPLE_RATE

        # cloud tasks
        case _ if path.startswith(tasks_decorator.CLOUD_TASK_SUBPATH):
            score = LOWEST_SAMPLE_RATE

        # All paths starting with "/public" are for public_api blueprint routes,
        # but not all of this blueprint routes start with "/public"
        case _ if path.startswith("/public"):
            score = LOWEST_SAMPLE_RATE
        # public V2 : "/v2"
        case _ if path.startswith(public_api_blueprints.DEPRECATED_PUBLIC_API_URL_PREFIX):
            score = LOWEST_SAMPLE_RATE

        # native routes
        case _ if path.startswith(UrlPrefix.NATIVE.value):
            score = LOWER_SAMPLE_RATE

        # Discord Auth
        case _ if path.startswith(UrlPrefix.AUTH.value):
            score = LOW_SAMPLE_RATE
        # adage V1
        case _ if path.startswith(UrlPrefix.ADAGE_V1.value):
            score = LOW_SAMPLE_RATE

        # SAML
        case _ if path.startswith(UrlPrefix.SAML.value):
            score = DEFAULT_SAMPLE_RATE
        # adage
        case _ if path.startswith(UrlPrefix.ADAGE_IFRAME.value):
            score = DEFAULT_SAMPLE_RATE

        # `Private API` or `pro_private_api` blueprints or a 404. We will filter them later
        case _:
            score = DEFAULT_SAMPLE_RATE

    return score


def filter_transactions(event: "Event", _hint: dict[str, typing.Any]) -> "Event | None":
    transaction = event.get("transaction")
    if transaction is None:
        return None

    match transaction:
        # backoffice
        case _ if transaction.startswith(backoffice_blueprint.BACKOFFICE_WEB_BLUEPRINT_NAME):
            sample_rate = DEFAULT_SAMPLE_RATE

        # private API "Private API"
        case _ if transaction.startswith(routes_apis.PRIVATE_API_BLUEPRINT_NAME):
            sample_rate = DEFAULT_SAMPLE_RATE
        # other private API "pro_private_api"
        case _ if transaction.startswith(pro_blueprint.PRO_PRIVATE_API_BLUEPRINT_NAME):
            sample_rate = DEFAULT_SAMPLE_RATE

        # Unmatched
        case _:
            sample_rate = LOWEST_SAMPLE_RATE

    # random.random is inclusive of 0, but not of 1, so strict < is safe here.
    return event if random.random() < sample_rate else None


def init_sentry_sdk() -> None:
    if not settings.ENABLE_SENTRY:
        return
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FlaskIntegration(), RedisIntegration(), RqIntegration(), SqlalchemyIntegration()],
        release=read_version_from_file(),
        environment=settings.ENV,
        traces_sample_rate=None if settings.ENABLE_SENTRY_FINE_SAMPLING else settings.SENTRY_DEFAULT_TRACES_SAMPLE_RATE,
        before_send=before_send,
        max_value_length=8192,
        traces_sampler=traces_sampler if settings.ENABLE_SENTRY_FINE_SAMPLING else None,
        before_send_transaction=filter_transactions if settings.ENABLE_SENTRY_FINE_SAMPLING else None,
    )


def get_custom_fingerprint(hint: dict[str, typing.Any]) -> str | None:
    if "exc_info" not in hint:
        return None

    _exc_type, exc_value, _traceback = hint["exc_info"]

    if isinstance(exc_value, ValidationError):
        return str(exc_value.errors())
    return None


def _is_flask_shell_event() -> bool:
    return bool(len(sys.argv) >= 2 and "flask" in sys.argv[0] and sys.argv[1] == "shell")
