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


def before_send(event: "Event", _hint: dict[str, typing.Any]) -> "Event | None":
    if _is_flask_shell_event():
        return None

    if custom_fingerprint := get_custom_fingerprint(_hint):
        event["fingerprint"] = ["{{ default }}", custom_fingerprint]
    return event


def init_sentry_sdk() -> None:
    if not settings.ENABLE_SENTRY:
        return
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FlaskIntegration(), RedisIntegration(), RqIntegration(), SqlalchemyIntegration()],
        release=read_version_from_file(),
        environment=settings.ENV,
        traces_sample_rate=settings.SENTRY_DEFAULT_TRACES_SAMPLE_RATE,
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
