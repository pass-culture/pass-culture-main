from functools import wraps
import json
import logging

from flask.blueprints import Blueprint
from flask.globals import request
import pydantic

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import requests

from . import cloud_task


CLOUD_TASK_SUBPATH = "/cloud-tasks"


logger = logging.getLogger(__name__)

cloud_task_api = Blueprint("Cloud task internal API", __name__, url_prefix=CLOUD_TASK_SUBPATH)


def task(queue: str, path: str, deduplicate: bool = False, delayed_seconds: int = 0):  # type: ignore [no-untyped-def]
    def decorator(f):  # type: ignore [no-untyped-def]
        payload_in_kwargs = f.__annotations__.get("payload")

        _define_handler(f, path, payload_in_kwargs)

        @wraps(f)
        def delay(payload: payload_in_kwargs):  # type: ignore [no-untyped-def]
            if settings.IS_RUNNING_TESTS:
                f(payload)
                return

            if isinstance(payload, pydantic.BaseModel):
                payload = json.loads(payload.json())  # type: ignore [attr-defined]

            cloud_task.enqueue_internal_task(
                queue, path, payload, deduplicate=deduplicate, delayed_seconds=delayed_seconds
            )

        f.delay = delay
        return f

    return decorator


def _define_handler(f, path, payload_type):  # type: ignore [no-untyped-def]
    @cloud_task_api.route(path, methods=["POST"], endpoint=path)
    @spectree_serialize(on_success_status=204)
    def handle_task(body: payload_type = None):  # type: ignore [no-untyped-def]
        queue_name = request.headers.get("HTTP_X_CLOUDTASKS_QUEUENAME")
        task_id = request.headers.get("HTTP_X_CLOUDTASKS_TASKNAME")
        retry_attempt = request.headers.get("X-CloudTasks-TaskRetryCount")

        job_details = {
            "queue": queue_name,
            "handler": path,
            "task": task_id,
            "body": request.get_json(),
            "retry_attempt": retry_attempt,
        }
        logger.info("Received cloud task %s", path, extra=job_details)

        if request.headers.get(cloud_task.AUTHORIZATION_HEADER_KEY) != cloud_task.AUTHORIZATION_HEADER_VALUE:
            logger.info("Unauthorized request on cloud task %s", path, extra=job_details)
            raise ApiErrors("Unauthorized", status_code=299)  # type: ignore [arg-type] # status code 2xx to prevent retry

        try:
            f(body)

        except requests.ExternalAPIException as exception:
            if not exception.is_retryable:
                # The task should not be retried as it would result with the same error again.
                # A log with a higher level should happen before.
                logger.warning("Task %s failed and should not be retried", path, extra=job_details)
                return

            if retry_attempt and int(retry_attempt) + 1 >= settings.CLOUD_TASK_MAX_ATTEMPTS:
                # notify that External API is probably unavailable
                logger.error(  # pylint: disable=logging-fstring-interpolation
                    f"External API unavailable for CloudTask {path}",
                    extra=job_details | {"exception": str(exception), "cause_exception": str(exception.__cause__)},
                )
            else:
                logger.warning(
                    "The cloud task has failed and will automatically be retried: %s",
                    path,
                    extra=job_details | {"exception": str(exception), "cause_exception": str(exception.__cause__)},
                )

            raise ApiErrors()

        except ApiErrors as e:
            logger.warning(
                "The task %s has not been executed successfully", path, extra={**job_details, "error": str(e)}
            )
            raise

        else:
            logger.info("Successfully executed cloud task %s", path, extra=job_details)
