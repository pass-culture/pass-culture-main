from typing import List

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

# When adding a task metric you should initialize it at 0 for all tasks by
# calling <metric_object>.labels(task="my-task")
metrics_list: List[Counter | Gauge | Histogram] = []
tasks_counter = Counter(
    "celery_tasks_total",
    "Total number of Celery tasks started",
    labelnames=["task"],
    registry=registry,
)
metrics_list += [tasks_counter]

tasks_in_progress = Gauge(
    "celery_tasks_in_progress", "Number of Celery tasks started running", labelnames=["task"], registry=registry
)
metrics_list += [tasks_in_progress]

tasks_succeeded_counter = Counter(
    "celery_tasks_succeeded_total",
    "Total number of Celery tasks that succeeded",
    labelnames=["task"],
    registry=registry,
)
metrics_list += [tasks_succeeded_counter]

tasks_failed_counter = Counter(
    "celery_tasks_failed_total",
    "Total number of Celery tasks started that failed",
    labelnames=["task"],
    registry=registry,
)
metrics_list += [tasks_failed_counter]

tasks_execution_time_histogram = Histogram(
    "celery_tasks_execution_time",
    "Time needed to run tasks",
    labelnames=["task"],
    registry=registry,
)
metrics_list += [tasks_execution_time_histogram]

tasks_rate_limited_counter = Counter(
    "celery_tasks_rate_limited",
    "Total number of Celery tasks started that were rate limited",
    labelnames=["task"],
    registry=registry,
)
metrics_list += [tasks_rate_limited_counter]


def start_metrics_server() -> None:
    start_http_server(settings.CELERY_WORKER_METRICS_PORT, registry=registry)
