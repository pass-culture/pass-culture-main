from dataclasses import dataclass
import json
from math import ceil
from unittest.mock import patch

import pytest

from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.scripts.external_users.unstack_batch_cloud_task_queue import unstack_batch_queue


pytestmark = pytest.mark.usefixtures("db_session")


@dataclass
class MockHttpRequest:
    body: bytes


@dataclass
class MockTask:
    def __init__(self, name, user_id):
        self.name = name

        body = json.dumps({"user_id": user_id}).encode("utf-8")
        self.http_request = MockHttpRequest(body)


@pytest.mark.parametrize("users_count,chunk_size", [(2, 3), (3, 1), (2, 2)])
@patch("pcapi.scripts.external_users.unstack_batch_cloud_task_queue.update_users_attributes")
@patch("pcapi.scripts.external_users.unstack_batch_cloud_task_queue.get_client")
def test_run_task_batch(mock_get_client, mock_update_users_attributes, users_count, chunk_size):
    users = BeneficiaryGrant18Factory.create_batch(users_count)
    mock_get_client.return_value.list_tasks.return_value = [MockTask(f"task_{user.id}", user.id) for user in users]

    tasks, deleted_tasks = unstack_batch_queue("some_queue_name", chunk_size)

    assert len(tasks) == len(deleted_tasks)
    assert len(tasks) == len(users)

    expected_call_count = ceil(len(users) / chunk_size)
    assert mock_update_users_attributes.call_count == expected_call_count
