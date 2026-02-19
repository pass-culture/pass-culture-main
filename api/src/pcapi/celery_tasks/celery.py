from celery import Celery
from celery import Task
from flask import Flask


def celery_init_app(app: Flask, *, task_with_app_context: bool = True) -> Celery:
    # Should be ok to only override the __call__ method
    # https://docs.celeryq.dev/en/stable/reference/celery.app.task.html#celery.app.task.Task
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    # in some case we do not need the app context in the task
    # e.g in the tests we already are in an app context and we run the tasks with "task_always_eager"
    task_class = FlaskTask if task_with_app_context else Task

    celery_app = Celery(app.name, task_cls=task_class)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
