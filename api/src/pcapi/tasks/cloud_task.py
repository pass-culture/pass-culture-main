from datetime import datetime
import hashlib
import json
import logging

from dateutil.relativedelta import relativedelta
from google.api_core import retry
from google.api_core.exceptions import AlreadyExists
from google.cloud import tasks_v2
from google.protobuf import duration_pb2  # type: ignore [import]
from google.protobuf import timestamp_pb2

from pcapi import settings
from pcapi.utils import requests


logger = logging.getLogger(__name__)


AUTHORIZATION_HEADER_KEY = "AUTHORIZATION"
AUTHORIZATION_HEADER_VALUE = f"Bearer {settings.CLOUD_TASK_BEARER_TOKEN}"
CLOUD_TASK_SUBPATH = "/cloud-tasks"


def get_client():  # type: ignore [no-untyped-def]
    if not hasattr(get_client, "client"):
        get_client.client = tasks_v2.CloudTasksClient()

    return get_client.client


def enqueue_task(
    queue: str,
    http_request: tasks_v2.HttpRequest,
    task_id: str | None = None,
    schedule_time: datetime | None = None,
    task_request_timeout: int | None = None,
) -> str | None:
    client = get_client()
    parent = client.queue_path(settings.GCP_PROJECT, settings.GCP_REGION_CLOUD_TASK, queue)

    task = tasks_v2.Task(http_request=http_request)

    # task_id must be used for de-duplication:
    # https://cloud.google.com/tasks/docs/reference/rest/v2/projects.locations.queues.tasks/create
    if task_id:
        task.name = client.task_path(settings.GCP_PROJECT, settings.GCP_REGION_CLOUD_TASK, queue, task_id)

    if schedule_time:
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(schedule_time)
        task.schedule_time = timestamp

    if task_request_timeout:
        # if the task request lasts more than this timeout, the task will be considered as failed (and may be retryied)
        # if not specified, google cloud tasks will use a default timeout of 10 minutes
        # https://cloud.google.com/tasks/docs/reference/rpc/google.cloud.tasks.v2#task
        task.dispatch_deadline = duration_pb2.Duration(seconds=task_request_timeout)

    task_request = tasks_v2.CreateTaskRequest(parent=parent, task=task)

    try:
        response = client.create_task(
            request=task_request,
            retry=retry.Retry(
                initial=settings.CLOUD_TASK_RETRY_INITIAL_DELAY,
                maximum=settings.CLOUD_TASK_RETRY_MAXIMUM_DELAY,
                multiplier=settings.CLOUD_TASK_RETRY_MULTIPLIER,
                deadline=settings.CLOUD_TASK_RETRY_DEADLINE,
            ),
        )
    except AlreadyExists:
        logger.info("Task on queue %s url %s already retried", queue, http_request.url)
        return None
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(
            "Failed to enqueue a task: %s",
            exc,
            extra={"queue": queue, "task_url": http_request.url, "body": http_request.body},
        )
        return None

    task_id = response.name.split("/")[-1]
    logger.info("Enqueued cloud task targetting %s", http_request.url, extra={"queue": queue, "task": task_id})

    return task_id


def enqueue_internal_task(queue, path, payload, deduplicate: bool = False, delayed_seconds: int = 0, task_request_timeout: int | None = None):  # type: ignore [no-untyped-def]
    url = settings.API_URL + CLOUD_TASK_SUBPATH + path

    if settings.IS_DEV:
        _call_internal_api_endpoint(queue, url, payload)
        return None

    http_request = tasks_v2.HttpRequest(
        body=json.dumps(payload).encode(),
        headers={"Content-type": "application/json", AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        http_method=tasks_v2.HttpMethod.POST,
        url=url,
    )

    # According to Google Cloud Tasks documentation, "Using hashed strings for the task id or for the prefix of the task
    # id is recommended".
    task_id = hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest() if deduplicate else None

    schedule_time = datetime.utcnow() + relativedelta(seconds=delayed_seconds) if delayed_seconds else None

    return enqueue_task(
        queue, http_request, task_id=task_id, schedule_time=schedule_time, task_request_timeout=task_request_timeout
    )


def _call_internal_api_endpoint(queue, url, payload):  # type: ignore [no-untyped-def]
    requests.post(
        url,
        headers={
            "HTTP_X_CLOUDTASKS_QUEUENAME": queue,
            AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE,
        },
        json=payload,
    )
