from functools import wraps
import json
import logging

from flask.blueprints import Blueprint
from flask.globals import request
from google.cloud import tasks_v2

from pcapi import settings
from pcapi.serialization.decorator import spectree_serialize


GCP_PROJECT = "passculture-metier-ehp"
GCP_LOCATION = "europe-west1"
CLOUD_TASK_SUBPATH = "/cloud-tasks"


logger = logging.getLogger(__name__)

cloud_task_api = Blueprint("Cloud task internal API", __name__, url_prefix=CLOUD_TASK_SUBPATH)

client = tasks_v2.CloudTasksClient()


def task(queue: str, path: str):
    def decorator(f):
        payload_in_kwargs = f.__annotations__.get("payload")

        _define_handler(f, path, payload_in_kwargs)

        @wraps(f)
        def delay(payload: payload_in_kwargs):
            task_id = _enqueue_task(queue, path, payload)
            logger.info("Enqueued cloud task", extra={"queue": queue, "handler": path, "task": task_id})

        f.delay = delay
        return f

    return decorator


def _define_handler(f, path, payload_type):
    @cloud_task_api.route(path, methods=["POST"])
    @spectree_serialize(on_success_status=204)
    def handle_task(body: payload_type):
        queue_name = request.headers.get("HTTP_X_CLOUDTASKS_QUEUENAME")
        task_id = request.headers.get("HTTP_X_CLOUDTASKS_TASKNAME")
        logger.info("Received cloud task", extra={"queue": queue_name, "handler": path, "task": task_id})

        try:
            f(body)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "Successfully executing cloud task",
                extra={"queue": queue_name, "handler": path, "task": task_id, "error": e},
            )
        else:
            logger.info(
                "Successfully executed cloud task", extra={"queue": queue_name, "handler": path, "task": task_id}
            )


def _enqueue_task(queue, path, payload):
    parent = client.queue_path(GCP_PROJECT, GCP_LOCATION, queue)

    url = settings.API_URL + CLOUD_TASK_SUBPATH + path
    body = json.dumps(payload).encode()

    task_request = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,
            "headers": {"Content-type": "application/json"},
            "body": body,
        },
    }

    response = client.create_task(request={"parent": parent, "task": task_request})

    task_id = response.name.split("/")[-1]
    return task_id
