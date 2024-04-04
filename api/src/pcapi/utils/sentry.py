import sys
import typing

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from pcapi import settings
from pcapi.utils.health_checker import read_version_from_file


if typing.TYPE_CHECKING:
    from sentry_sdk.types import Event


def ignore_flask_shell_event(event: "Event", _hint: dict[str, typing.Any]) -> "Event | None":
    if len(sys.argv) >= 2 and "flask" in sys.argv[0] and sys.argv[1] == "shell":
        return None
    return event


def init_sentry_sdk() -> None:
    if settings.IS_DEV:
        return
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FlaskIntegration(), RedisIntegration(), RqIntegration(), SqlalchemyIntegration()],
        release=read_version_from_file(),
        environment=settings.ENV,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        before_send=ignore_flask_shell_event,
        max_value_length=8192,
    )
