from pcapi import settings
from pcapi.celery_tasks import metrics
from pcapi.celery_tasks import sendinblue  # noqa: F401
from pcapi.core.offers import tasks  # noqa: F401
from pcapi.flask_app import app as flask_app


if settings.CELERY_WORKER_ENABLE_METRICS:
    metrics.start_metrics_server()

celery_app = flask_app.extensions["celery"]
registered_tasks = sorted(task for task in celery_app.tasks.keys() if not task.startswith("celery"))

# Initialize metrics with 0 value but with correct labels
for task in registered_tasks:
    for metric in metrics.metrics_list:
        metric.labels(task=task)
