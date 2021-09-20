from functools import wraps
import json
import logging

from flask.blueprints import Blueprint
from flask.globals import request
import pydantic

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
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

            if isinstance(payload, pydantic.BaseModel):
                payload = json.loads(payload.json())

            task_id = cloud_task.enqueue_internal_task(queue, path, payload)
            logger.info("Enqueued cloud task %s", path, extra={"queue": queue, "handler": path, "task": task_id})

        f.delay = delay
        return f

    return decorator


def _define_handler(f, path, payload_type):
    @cloud_task_api.route(path, methods=["POST"], endpoint=path)
    @spectree_serialize(on_success_status=204)
    def handle_task(body: payload_type = None):
        queue_name = request.headers.get("HTTP_X_CLOUDTASKS_QUEUENAME")
        task_id = request.headers.get("HTTP_X_CLOUDTASKS_TASKNAME")

        job_details = {"queue": queue_name, "handler": path, "task": task_id, "body": request.get_json()}
        logger.info("Received cloud task %s", path, extra=job_details)

        if request.headers.get(cloud_task.AUTHORIZATION_HEADER_KEY) != cloud_task.AUTHORIZATION_HEADER_VALUE:
            logger.info("Unauthorized request on cloud task %s", path, extra=job_details)
            raise ApiErrors("Unauthorized", status_code=299)  # status code 2xx to prevent retry

        try:
            f(body)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "Exception caught when executing cloud task %s", path, extra={**job_details, "error": str(e)}
            )
        else:
            logger.info("Successfully executed cloud task %s", path, extra=job_details)
