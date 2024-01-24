import logging
import os
import re
import sys
import typing

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from pcapi import settings
from pcapi.utils.health_checker import read_version_from_file


# Do not suppress warnings
# https://docs.python.org/3/library/warnings.html#the-warnings-filter
os.environ["PYTHONWARNINGS"] = "default"

# Redirect all warnings to the logging library
logging.captureWarnings(True)

# Parse usefull part of SQLAlchemy warnings
parse_sqla_warnings = re.compile(r"^.*src\/pcapi\/(?P<usefull_part>.*: [\w]+Warning.*)")


def before_send(event: dict[str, typing.Any], _hint: dict[str, typing.Any]) -> dict[str, typing.Any] | None:
    # Ignore flask shell events
    if len(sys.argv) >= 2 and "flask" in sys.argv[0] and sys.argv[1] == "shell":
        return None

    # Ignore all warnings except ones from SQLAlchemy
    if (
        "SAWarning" not in event["logentry"]["message"]
        and "RemovedIn20Warning" not in event["logentry"]["message"]
        and "LegacyAPIWarning" not in event["logentry"]["message"]
    ):
        return None
    if (
        "SAWarning" in event["logentry"]["message"]
        or "RemovedIn20Warning" in event["logentry"]["message"]
        or "LegacyAPIWarning" in event["logentry"]["message"]
    ):
        # Truncate useless part of the path in the warning
        message = event["logentry"]["message"]
        match = re.match(parse_sqla_warnings, message)
        if match is not None:
            event["logentry"]["message"] = match["usefull_part"]
        return event

    return event


def init_sentry_sdk() -> None:
    if settings.IS_DEV:
        return
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FlaskIntegration(),
            RedisIntegration(),
            RqIntegration(),
            SqlalchemyIntegration(),
            # https://docs.sentry.io/platforms/python/integrations/logging/
            # Make Sentry capture warning logs
            LoggingIntegration(level=logging.INFO, event_level=logging.WARNING),
        ],
        release=read_version_from_file(),
        environment=settings.ENV,
        traces_sample_rate=settings.SENTRY_SAMPLE_RATE,
        before_send=before_send,
        max_value_length=8192,
    )
