import os

from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import multiprocess
from prometheus_client import start_http_server


if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
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
    start_http_server(8080, registry=registry)
