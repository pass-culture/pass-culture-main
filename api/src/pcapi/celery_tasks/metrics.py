import json
from typing import Iterator
from typing import List

from prometheus_client import REGISTRY
from prometheus_client import CollectorRegistry
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import multiprocess
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from pcapi import settings
from pcapi.celery_tasks.config import CELERY_QUEUE_NAMES


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


class PendingTaskCollector(Collector):
    def collect(self) -> Iterator[GaugeMetricFamily]:
        gauge = GaugeMetricFamily(
            "celery_pending_tasks", "Number of Celery tasks that are currently pending", labels=["task"]
        )

        if not settings.CELERY_MONITORED_QUEUES:
            # local development only spawns one celery pod that handles all queues
            monitored_queues = CELERY_QUEUE_NAMES
        else:
            monitored_queues = [queue for queue in CELERY_QUEUE_NAMES if queue in settings.CELERY_MONITORED_QUEUES]

        for queue in monitored_queues:
            for task_name, count in _count_pending_tasks(queue).items():
                gauge.add_metric([task_name], count)

        yield gauge


def _count_pending_tasks(queue_name: str) -> dict[str, int]:
    # avoid (flask_app -> celery_init_app -> celery -> metrics -> flask_app)  circular import
    from pcapi.flask_app import app as flask_app

    PENDING_TASKS_SCAN_LIMIT = 10_000
    counts: dict[str, int] = {}
    for raw_message in flask_app.redis_client.lrange(queue_name, 0, PENDING_TASKS_SCAN_LIMIT - 1):
        try:
            task_name = json.loads(raw_message)["headers"]["task"]
        except (json.JSONDecodeError, KeyError, TypeError):
            continue
        counts[task_name] = counts.get(task_name, 0) + 1
    return counts


def start_metrics_server() -> None:
    registry.register(PendingTaskCollector())
    start_http_server(settings.CELERY_WORKER_METRICS_PORT, registry=registry)
