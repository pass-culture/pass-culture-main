from pcapi import settings
from pcapi.celery_tasks import metrics
from pcapi.celery_tasks import sendinblue  # noqa: F401
from pcapi.core.offers import tasks  # noqa: F401
from pcapi.flask_app import app as flask_app


if settings.CELERY_WORKER_ENABLE_METRICS:
    metrics.start_metrics_server()

celery_app = flask_app.extensions["celery"]
