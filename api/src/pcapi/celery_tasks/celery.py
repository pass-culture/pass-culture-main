from celery import Celery
from celery import Task
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    # Should be ok to only override the __call__ method
    # https://docs.celeryq.dev/en/stable/reference/celery.app.task.html#celery.app.task.Task
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
