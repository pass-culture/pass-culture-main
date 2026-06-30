import json

import pytest
from prometheus_client import CollectorRegistry

import pcapi.celery_tasks.metrics as metrics
from pcapi.celery_tasks import config as celery_config
from pcapi.celery_tasks.tasks import celery_async_task


success_task_name = "tasks.tests.success"
failure_task_name = "tasks.tests.failure"


@celery_async_task(name=success_task_name, model=None)
def success_task(payload: None) -> None:
    pass


@celery_async_task(name="tasks.tests.failure", model=None)
def failure_task(payload: None) -> None:
    raise Exception


class TaskCounterTest:
    metric_name = "celery_tasks_total"

    def test_counter_augmented_on_task_success(self):
        before = metrics.registry.get_sample_value(self.metric_name, labels={"task": success_task_name})
        if before is None:
            before = 0
        success_task.delay(None)
        after = metrics.registry.get_sample_value(self.metric_name, labels={"task": success_task_name})
        assert after == before + 1

    def test_counter_augmented_on_task_failure(self):
        before = metrics.registry.get_sample_value(self.metric_name, labels={"task": failure_task_name})
        if before is None:
            before = 0
        try:
            failure_task.delay(None)
        except Exception:
            pass
        after = metrics.registry.get_sample_value(self.metric_name, labels={"task": failure_task_name})
        assert after == before + 1


class PendingTasksCollectorTest:
    metric_name = "celery_pending_tasks"

    def test_counts_pending_tasks_per_task_name(self, app):
        queue_name = celery_config.CELERY_EXTERNAL_CALLS_DEFAULT_QUEUE_NAME
        task_name = "tasks.tests.pending"

        message = json.dumps({"headers": {"task": task_name}, "body": "", "properties": {}})
        app.redis_client.rpush(queue_name, message)
        app.redis_client.rpush(queue_name, message)

        registry = CollectorRegistry()
        registry.register(metrics.PendingTaskCollector())
        pending_count = registry.get_sample_value(self.metric_name, labels={"task": task_name})
        assert pending_count == 2

    @pytest.mark.settings(CELERY_MONITORED_QUEUES=celery_config.CELERY_INTERNAL_CALLS_PRIORITY_QUEUE_NAME)
    def test_counts_pending_tasks_ignores_other_queues(self, app):
        task_name = "tasks.tests.pending"

        message = json.dumps({"headers": {"task": "tasks.tests.pending"}, "body": "", "properties": {}})
        app.redis_client.rpush(celery_config.CELERY_EXTERNAL_CALLS_DEFAULT_QUEUE_NAME, message)

        registry = CollectorRegistry()
        registry.register(metrics.PendingTaskCollector())
        pending_count = registry.get_sample_value(self.metric_name, labels={"task": task_name})
        assert pending_count is None

    def test_empty_queue_reports_no_series(self, app):
        registry = CollectorRegistry()
        registry.register(metrics.PendingTaskCollector())
        pending_count = registry.get_sample_value(self.metric_name, labels={"task": "not-found"})
        assert pending_count is None

    def test_unparseable_messages_are_ignored(self, app):
        queue_name = celery_config.CELERY_EXTERNAL_CALLS_DEFAULT_QUEUE_NAME
        task_name = "tasks.tests.pending"

        app.redis_client.rpush(queue_name, "not-json")

        registry = CollectorRegistry()
        registry.register(metrics.PendingTaskCollector())
        pending_count = registry.get_sample_value(self.metric_name, labels={"task": task_name})
        assert pending_count is None
