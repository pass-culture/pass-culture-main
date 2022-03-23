from dataclasses import dataclass
import itertools
import json
import logging
from time import sleep
import typing
from typing import Generator

from google.cloud.tasks_v2 import CloudTasksClient
from google.cloud.tasks_v2.types import Task

from pcapi import settings
from pcapi.core.users.external import batch as batch_operations
from pcapi.core.users.external import get_user_attributes
from pcapi.core.users.models import User
from pcapi.notifications.push import update_users_attributes
from pcapi.notifications.push.backends import batch as batch_backend


logger = logging.getLogger(__name__)


@dataclass
class UserTask:
    user_id: int
    task_name: str


UsersTaskGenerator = typing.Generator[UserTask, None, None]


def get_users_task_chunks(users_tasks: UsersTaskGenerator, chunk_size: int) -> Generator[list[UserTask], None, None]:
    """
    Build chunks of UserTask from UserTask generator
    """
    while True:
        chunk = list(itertools.islice(users_tasks, chunk_size))
        if chunk:
            yield chunk

        if len(chunk) < chunk_size:
            break


def format_batch_users(users: list[User]) -> list[batch_backend.UserUpdateData]:
    """
    Format user data for the request to the Batch API
    """
    res = []
    for user in users:
        attributes = batch_operations.format_user_attributes(get_user_attributes(user))
        res.append(batch_backend.UserUpdateData(user_id=str(user.id), attributes=attributes))
    print(f"{len(res)} users formatted for batch...")
    return res


def get_client() -> CloudTasksClient:
    return CloudTasksClient()


def fetch_user_ids_from_tasks(client: CloudTasksClient, parent: str) -> UsersTaskGenerator:
    """
    Extract user ids from a Cloud Tasks' queue's tasks
    """
    request = {
        "parent": parent,
        "response_view": Task.View.FULL,
    }

    for task in client.list_tasks(request=request):
        try:
            payload = json.loads(task.http_request.body)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to parse task's http request's body", extra={"task": task.name})
        else:
            yield UserTask(user_id=payload["user_id"], task_name=task.name)


def delete_tasks(client: CloudTasksClient, task_names: set[str]) -> set[str]:
    deleted_tasks = set()

    for task_name in task_names:
        try:
            client.delete_task(name=task_name)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to delete task", extra={"task": task_name})
        else:
            deleted_tasks.add(task_name)

    print(f"deleted {len(deleted_tasks)} / {len(task_names)} tasks")
    return deleted_tasks


def unstack_batch_queue(queue_name: str, chunk_size: int = 1_000, sleep_time: float = 2.0) -> tuple[set[str], set[str]]:
    """
    Process update user attributes tasks from Cloud task queue:

        * fetch tasks information from a Cloud Task queue,
        * extract user ids from it,
        * call Batch API to update users attributes,
        * delete tasks from the queue.

    Notes:
        This function should be called when the queue is paused.
        Check out Google's documentation for more information:
            https://cloud.google.com/python/docs/reference/cloudtasks/latest/google.cloud.tasks_v2.services.cloud_tasks.CloudTasksClient

    Args:
        queue_name: queue name (not full path, only the name)
        chunk_size: number of users per request to the Batch API,
                    defaults to 1_000 (Batch API's max value accepted)
        sleep_time: sleep time in seconds, between to request to the
                    Batch API (avoids spamming the API)

    Returns:
        2-item tuple: 1) set of extracted tasks names, 2) set of deleted
        tasks names. If nothing went wront both should be equal.
    """
    print("Starting...")

    client = get_client()
    tasks_to_delete = set()

    parent = client.queue_path(settings.GCP_PROJECT, settings.GCP_REGION_CLOUD_TASK, queue_name)
    for users_task_chunk in get_users_task_chunks(fetch_user_ids_from_tasks(client, parent), chunk_size):
        try:
            user_ids = {item.user_id for item in users_task_chunk}
            users = User.query.filter(User.id.in_(user_ids)).all()
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to fetch users from chunk", extra={"chunk_size": len(users_task_chunk)})
            continue

        try:
            batch_users_data = format_batch_users(users)
            update_users_attributes(batch_users_data)
        except Exception:  # pylint: disable=broad-except  # pylint: disable=broad-except
            logger.exception("Failed to update users attributes", extra={"chunk_size": len(users_task_chunk)})
            continue

        tasks_to_delete |= {item.task_name for item in users_task_chunk}
        print(f"chunk of {len(users_task_chunk)} users... done")

        sleep(sleep_time)

    deleted_tasks = delete_tasks(client, tasks_to_delete)
    print("End")

    return tasks_to_delete, deleted_tasks
