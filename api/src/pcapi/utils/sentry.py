import logging
import sys
import typing

from pydantic.v1 import ValidationError
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from pcapi import settings
from pcapi.utils.health_checker import read_version_from_file


if typing.TYPE_CHECKING:
    from sentry_sdk.types import Event

logger = logging.getLogger(__name__)


DEFAULT_SAMPLING_RATE = settings.SENTRY_TRACES_SAMPLE_RATE
LOW_SAMPLING_RATE = DEFAULT_SAMPLING_RATE / 10
LOWER_SAMPLING_RATE = DEFAULT_SAMPLING_RATE / 100
LOWEST_SAMPLING_RATE = DEFAULT_SAMPLING_RATE / 1000
NO_SAMPLING_RATE = 0.0


def before_send(event: "Event", _hint: dict[str, typing.Any]) -> "Event | None":
    if _is_flask_shell_event():
        return None

    if custom_fingerprint := get_custom_fingerprint(_hint):
        event["fingerprint"] = ["{{ default }}", custom_fingerprint]
    return event


def traces_sampler(sampling_context: dict) -> float:
    """
    This sampler defines a fraction of the DEFAULT_SAMPLING_RATE according to the transaction name
    """
    transaction_context = sampling_context.get("transaction_context")
    if transaction_context is None:
        logger.info("[sentry traces_sampler] No transaction_context", extra={"sampling_context": sampling_context})
        return NO_SAMPLING_RATE

    name = transaction_context.get("name")
    # Each Flask app Blueprint name should be in this pattern matching
    # From lowest to standard sampling rates
    match name:
        # static files for BO
        case "static":
            return LOWEST_SAMPLING_RATE
        # monitoring endpoints
        case _ if name.endswith("health_api"):
            return LOWEST_SAMPLING_RATE
        case _ if name.endswith("health_database"):
            return LOWEST_SAMPLING_RATE
        # cloud tasks
        case _ if name.startswith("Cloud task internal API"):
            return LOWEST_SAMPLING_RATE
        # public
        case _ if name.startswith("public_blueprint"):
            return LOWEST_SAMPLING_RATE
        # public V2
        case _ if name.startswith("pro_public_api_v2"):
            return LOWEST_SAMPLING_RATE
        # native routes
        case _ if name.startswith("native"):
            return LOWER_SAMPLING_RATE
        # deprecated public API
        case _ if name.startswith("Public API"):
            return LOWER_SAMPLING_RATE
        # adage
        case _ if name.startswith("adage_v1"):
            return LOW_SAMPLING_RATE
        # SAML
        case _ if name.startswith("saml_blueprint"):
            return LOW_SAMPLING_RATE
        # adage
        case _ if name.startswith("adage_iframe"):
            return DEFAULT_SAMPLING_RATE
        # backoffice
        case _ if name.startswith("backoffice_web"):
            return DEFAULT_SAMPLING_RATE
        # private API
        case _ if name.startswith("Private API"):
            return DEFAULT_SAMPLING_RATE
        # other private API
        case _ if name.startswith("pro_private_api"):
            return DEFAULT_SAMPLING_RATE
        # Unmatched or None
        case _:
            logger.info("[sentry traces_sampler] Could not match transaction name", extra={"transaction_name": name})
            return LOWEST_SAMPLING_RATE


def init_sentry_sdk() -> None:
    if settings.IS_DEV:
        return
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FlaskIntegration(), RedisIntegration(), RqIntegration(), SqlalchemyIntegration()],
        release=read_version_from_file(),
        environment=settings.ENV,
        traces_sampler=traces_sampler,
        before_send=before_send,
        max_value_length=8192,
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
