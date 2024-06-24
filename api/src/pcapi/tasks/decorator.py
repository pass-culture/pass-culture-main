from functools import wraps
import json
import logging
import typing

from flask.blueprints import Blueprint
from flask.globals import request
import pydantic.v1 as pydantic_v1

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import requests

from . import cloud_task


CLOUD_TASK_SUBPATH = "/cloud-tasks"


logger = logging.getLogger(__name__)

cloud_task_api = Blueprint("Cloud task internal API", __name__, url_prefix=CLOUD_TASK_SUBPATH)


def task(
    queue: str,
    path: str,
    deduplicate: bool = False,
    delayed_seconds: int = 0,
    task_request_timeout: int | None = None,
) -> typing.Callable:
    def decorator(f: typing.Callable) -> typing.Callable:
        payload_type = f.__annotations__["payload"]
        assert issubclass(payload_type, pydantic_v1.BaseModel)

        _define_handler(f, path, payload_type)

        @wraps(f)
        def delay(payload: pydantic_v1.BaseModel) -> None:
            if settings.IS_JOB_SYNCHRONOUS:
                f(payload)
                return

            payload = json.loads(payload.json())

            cloud_task.enqueue_internal_task(
                queue,
                path,
                payload,
                deduplicate=deduplicate,
                delayed_seconds=delayed_seconds,
                task_request_timeout=task_request_timeout,
            )

        f.delay = delay  # type: ignore[attr-defined]
        return f

    return decorator


def _define_handler(
    f: typing.Callable,
    path: str,
    payload_type: type[pydantic_v1.BaseModel],
) -> None:
    @cloud_task_api.route(path, methods=["POST"], endpoint=path)
    @spectree_serialize(on_success_status=204)
    def handle_task(body: payload_type) -> None:  # type: ignore[valid-type]
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
            raise ApiErrors("Unauthorized", status_code=299)  # type: ignore[arg-type] # status code 2xx to prevent retry

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

        logger.info("Successfully executed cloud task %s", path, extra=job_details)
