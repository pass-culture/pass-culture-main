import pcapi.celery_tasks.metrics as metrics
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
