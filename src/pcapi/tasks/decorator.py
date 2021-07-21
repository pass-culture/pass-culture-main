from functools import wraps
import logging

from flask.blueprints import Blueprint
from flask.globals import request
import requests

from pcapi import settings
from pcapi.serialization.decorator import spectree_serialize

from . import cloud_task


CLOUD_TASK_SUBPATH = "/cloud-tasks"


logger = logging.getLogger(__name__)

cloud_task_api = Blueprint("Cloud task internal API", __name__, url_prefix=CLOUD_TASK_SUBPATH)


def task(queue: str, path: str):
    def decorator(f):
        payload_in_kwargs = f.__annotations__.get("payload")

        _define_handler(f, path, payload_in_kwargs)

        @wraps(f)
        def delay(payload: payload_in_kwargs):
            if settings.IS_RUNNING_TESTS:
                f(payload)
                return

            task_id = _enqueue_task(queue, path, payload)
            logger.info("Enqueued cloud task", extra={"queue": queue, "handler": path, "task": task_id})

        f.delay = delay
        return f

    return decorator


def _define_handler(f, path, payload_type):
    @cloud_task_api.route(path, methods=["POST"], endpoint=path)
    @spectree_serialize(on_success_status=204)
    def handle_task(body: payload_type):
        queue_name = request.headers.get("HTTP_X_CLOUDTASKS_QUEUENAME")
        task_id = request.headers.get("HTTP_X_CLOUDTASKS_TASKNAME")
        job_details = {"queue": queue_name, "handler": path, "task": task_id, "body": request.get_json()}
        logger.info("Received cloud task", extra=job_details)

        try:
            f(body)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Exception caught when executing cloud task", extra={**job_details, "error": e})
        else:
            logger.info("Successfully executed cloud task", extra=job_details)


def _enqueue_task(queue, path, payload):
    url = settings.API_URL + CLOUD_TASK_SUBPATH + path

    if settings.IS_DEV:
        _call_task_handler(queue, url, payload)
        return None

    return cloud_task.enqueue_task(queue, url, payload)


def _call_task_handler(queue, url, payload):
    requests.post(
        url,
        headers={
            "HTTP_X_CLOUDTASKS_QUEUENAME": queue,
        },
        json=payload,
    )
