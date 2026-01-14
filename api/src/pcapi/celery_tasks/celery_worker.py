import logging
import typing

from celery import signals

import pcapi.celery_tasks.sendinblue  # noqa: F401
import pcapi.core.educational.tasks  # noqa: F401
import pcapi.core.external.zendesk.tasks  # noqa: F401
import pcapi.core.offers.tasks  # noqa: F401
import pcapi.core.operations.tasks  # noqa: F401
import pcapi.core.subscription.bonus.tasks  # noqa: F401
import pcapi.core.subscription.ubble.tasks  # noqa: F401
from pcapi import settings
from pcapi.celery_tasks import metrics
from pcapi.core.logging import JsonFormatter
from pcapi.flask_app import app as flask_app


if settings.CELERY_WORKER_ENABLE_METRICS:
    metrics.start_metrics_server()

celery_app = flask_app.extensions["celery"]
registered_tasks = sorted(task for task in celery_app.tasks.keys() if not task.startswith("celery"))

# Initialize metrics with 0 value but with correct labels
for task in registered_tasks:
    for metric in metrics.metrics_list:
        metric.labels(task=task)


@signals.after_setup_logger.connect
def setup_logger(logger: logging.Logger, *args: typing.Any, **kwargs: typing.Any) -> None:
    """
    This function runs when the Celery worker initializes its logging.
    We replace the default handler with a JSON-formatted one.
    """
    formatter = JsonFormatter()
    for handler in logger.handlers:
        handler.setFormatter(formatter)
