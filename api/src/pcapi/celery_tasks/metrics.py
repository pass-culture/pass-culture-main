from prometheus_client import REGISTRY
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import multiprocess
from prometheus_client import start_http_server

from pcapi import settings


if settings.PROMETHEUS_MULTIPROC_DIR:
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
else:
    registry = REGISTRY

tasks_counter = Counter(
    "celery_tasks_total",
    "Total number of Celery tasks started",
    labelnames=["task"],
    registry=registry,
)
tasks_in_progress = Gauge(
    "celery_tasks_in_progress", "Number of Celery tasks started running", labelnames=["task"], registry=registry
)
tasks_succeeded_counter = Counter(
    "celery_tasks_succeeded_total",
    "Total number of Celery tasks that succeeded",
    labelnames=["task"],
    registry=registry,
)
tasks_failed_counter = Counter(
    "celery_tasks_failed_total",
    "Total number of Celery tasks started that failed",
    labelnames=["task"],
    registry=registry,
)
tasks_execution_time_histogram = Histogram(
    "celery_tasks_execution_time",
    "Time needed to run tasks",
    labelnames=["task"],
    registry=registry,
)


def start_metrics_server() -> None:
    start_http_server(settings.CELERY_WORKER_METRICS_PORT, registry=registry)
