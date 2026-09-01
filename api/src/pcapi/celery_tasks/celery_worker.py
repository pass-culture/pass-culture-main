import logging
import typing

from celery import signals

import pcapi.core.cultural_survey.tasks
import pcapi.core.educational.tasks
import pcapi.core.external.batch.tasks
import pcapi.core.external.compliance.tasks
import pcapi.core.external.zendesk.tasks
import pcapi.core.external.zendesk_sell.tasks
import pcapi.core.finance.tasks
import pcapi.core.mails.tasks
import pcapi.core.offerers.tasks
import pcapi.core.offers.tasks
import pcapi.core.operations.tasks
import pcapi.core.providers.tasks
import pcapi.core.subscription.bonus.tasks
import pcapi.core.subscription.ubble.tasks  # noqa: F401
from pcapi import settings
from pcapi.celery_tasks import metrics
from pcapi.core.logging import JsonFormatter
from pcapi.flask_app import app as flask_app


if settings.CELERY_WORKER_ENABLE_METRICS:
    metrics.start_metrics_server()

celery_app = flask_app.extensions["celery"]
registered_tasks = sorted(task for task in celery_app.tasks if not task.startswith("celery"))

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
