import enum
import random
import sys
import typing

import sentry_sdk
from pydantic.v1 import ValidationError
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

import pcapi.routes.apis as routes_apis
import pcapi.routes.backoffice.blueprint as backoffice_blueprint
import pcapi.routes.pro.blueprint as pro_blueprint
import pcapi.tasks.decorator as tasks_decorator
from pcapi import settings
from pcapi.routes import UrlPrefix
from pcapi.utils.health_checker import read_version_from_file


if typing.TYPE_CHECKING:
    from sentry_sdk.types import Event


DEFAULT_SAMPLE_RATE = settings.SENTRY_DEFAULT_TRACES_SAMPLE_RATE
LOW_SAMPLE_RATE = DEFAULT_SAMPLE_RATE / 10
LOWER_SAMPLE_RATE = DEFAULT_SAMPLE_RATE / 100
LOWEST_SAMPLE_RATE = DEFAULT_SAMPLE_RATE / 1000
NO_SAMPLE_RATE = 0.0

SCRUBBED_INFO_PLACEHOLDER = "[REDACTED]"

SCRUBBED_KEYS = (
    "anneeDateNaissance",
    "all_quotient_familial_responses",
    "codeCogInseeCommuneNaissance",
    "codeCogInseePaysNaissance",
    "custodian",
    "jourDateNaissance",
    "moisDateNaissance",
    "nomNaissance",
    "nomUsage",
    "prenoms[]",
    "recipient",
    "sexeEtatCivil",
    "quotient_familial_response",
    "recipient",
)

SCRUBBED_VALUE_PREFIXES = ("QuotientFamilialBonusCreditContent(",)


class SpecificPath(enum.Enum):
    BACKOFFICE_HOME = f"{backoffice_blueprint.BACKOFFICE_WEB_BLUEPRINT_NAME}.home"
    PRO_AUTOLOGIN_SIGNUP = "/users/validate_signup/"


def scrub_token_from_url_in_event(event: "Event") -> "Event":
    full_url = str(event.get("request", {}).get("url"))
    if SpecificPath.PRO_AUTOLOGIN_SIGNUP.value in full_url:
        token_start = full_url.rfind("/") + 1
        event["request"]["url"] = full_url[:token_start] + SCRUBBED_INFO_PLACEHOLDER
    return event


def recursive_scrub_vars_dict(vars_dict: dict) -> dict:
    r"""
    Recursively obfuscate values inside `vars_dict` if their associated key is in `redacted_fields` list.

    /!\ This function does modify values of source `vars_dict`
    """
    for key in list(vars_dict):
        value = vars_dict[key]
        if key in SCRUBBED_KEYS:
            vars_dict[key] = SCRUBBED_INFO_PLACEHOLDER
        elif isinstance(value, str) and any(value.startswith(prefix) for prefix in SCRUBBED_VALUE_PREFIXES):
            vars_dict[key] = SCRUBBED_INFO_PLACEHOLDER
        if isinstance(value, dict):
            vars_dict[key] = recursive_scrub_vars_dict(value)
    return vars_dict


def before_send(event: "Event", _hint: dict[str, typing.Any]) -> "Event | None":
    if _is_flask_shell_event():
        return None

    scrub_token_from_url_in_event(event)

    if custom_fingerprint := get_custom_fingerprint(_hint):
        event["fingerprint"] = ["{{ default }}", custom_fingerprint]

    # Scrub exceptions vars
    for exception_values in event.get("exception", {}).get("values", []):
        for frame in exception_values.get("stacktrace", {}).get("frames", []):
            if frame_vars := frame.get("vars"):
                recursive_scrub_vars_dict(frame_vars)

    return event


def custom_traces_sampler(sampling_context: dict) -> float:
    """
    This sampler defines a fraction of the DEFAULT_SAMPLE_RATE according to the requested path
    The sentry SDK will then apply that rate to decide if the transaction should be sampled
    At this time, the transaction name has not yet been defined by Flask, but we will later filter out
    some events in before_send_transaction()
    """
    path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO")

    # for instance : worker requests
    if not path or not isinstance(path, str):
        return LOWEST_SAMPLE_RATE

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


def before_send_transaction(event: "Event", _hint: dict[str, typing.Any]) -> "Event | None":
    """When we return None, the event is dropped and won't be send to Sentry so no need to remove info"""
    if not settings.SENTRY_FINE_SAMPLING:
        return None
    filtered_event = filter_transactions(event, _hint)
    if filtered_event:
        return scrub_token_from_url_in_event(filtered_event)
    return None


def filter_transactions(event: "Event", _hint: dict[str, typing.Any]) -> "Event | None":
    transaction = event.get("transaction")

    if not transaction:
        return None

    match transaction:
        # BO home
        case SpecificPath.BACKOFFICE_HOME.value:
            sample_rate = NO_SAMPLE_RATE

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
        integrations=[
            CeleryIntegration(),
            FlaskIntegration(),
            RedisIntegration(),
            RqIntegration(),
            SqlalchemyIntegration(),
        ],
        release=read_version_from_file(),
        environment=settings.ENV,
        traces_sample_rate=None if settings.SENTRY_FINE_SAMPLING else settings.SENTRY_DEFAULT_TRACES_SAMPLE_RATE,
        before_send=before_send,
        max_value_length=8192,
        traces_sampler=custom_traces_sampler if settings.SENTRY_FINE_SAMPLING else None,
        before_send_transaction=before_send_transaction,
    )
    # TODO(fseguin-pass, 2025-01-07) drop when all envs are moved
    sentry_sdk.set_tag(key="pcapi.is_new_infra", value=str(settings.IS_NEW_INFRA))


def get_custom_fingerprint(hint: dict[str, typing.Any]) -> str | None:
    if "exc_info" not in hint:
        return None

    _exc_type, exc_value, _traceback = hint["exc_info"]

    if isinstance(exc_value, ValidationError):
        return str(exc_value.errors())
    return None


def _is_flask_shell_event() -> bool:
    return bool(len(sys.argv) >= 2 and "flask" in sys.argv[0] and sys.argv[1] == "shell")
