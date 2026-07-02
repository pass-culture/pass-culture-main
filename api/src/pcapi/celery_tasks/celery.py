from celery import Celery
from celery import Task
from celery.utils.saferepr import saferepr
from flask import Flask


# avoid importing utils.sentry because it pulls route blueprints
REDACTED_PII_PLACEHOLDER = "[REDACTED]"


def scrub_pii(value: object, pii_fields: frozenset[str]) -> object:
    """Deep copy value, scrubbing any dict fields present in pii_fields.
    It never mutates the input that is passed as is to the worker."""
    if isinstance(value, dict):
        return {
            key: REDACTED_PII_PLACEHOLDER if key in pii_fields else scrub_pii(sub_value, pii_fields)
            for key, sub_value in value.items()
        }
    if isinstance(value, (list, tuple)):
        return type(value)(scrub_pii(item, pii_fields) for item in value)
    return value


class _RedactPiiInLogsTask(Task):
    pii_fields: frozenset[str] | None = None

    def apply_async(self, args: tuple | None = None, kwargs: dict | None = None, **options: object) -> object:
        if self.pii_fields:
            options["argsrepr"] = saferepr(scrub_pii(args or (), self.pii_fields))
            options["kwargsrepr"] = saferepr(scrub_pii(kwargs or (), self.pii_fields))
        # very uncanny, args and kwargs are regular positional arguments
        return super().apply_async(args, kwargs, **options)


def celery_init_app(app: Flask, *, task_with_app_context: bool = True) -> Celery:
    # Should be ok to only override the __call__ method
    # https://docs.celeryq.dev/en/stable/reference/celery.app.task.html#celery.app.task.Task
    class FlaskTask(_RedactPiiInLogsTask):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    # in some case we do not need the app context in the task
    # e.g in the tests we already are in an app context and we run the tasks with "task_always_eager"
    task_class = FlaskTask if task_with_app_context else _RedactPiiInLogsTask

    celery_app = Celery(app.name, task_cls=task_class)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
