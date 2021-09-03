from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

from google.cloud import tasks_v2
from pydantic import BaseModel
import pytest

from pcapi import settings
from pcapi.core.testing import override_settings
from pcapi.models import ApiErrors
from pcapi.tasks.decorator import task

from tests.conftest import TestClient


def generate_task(f):
    TEST_QUEUE = "test-queue"

    class VoidTaskPayload(BaseModel):
        chouquette_price: int

    @task(TEST_QUEUE, "/void_task")
    def test_task(payload: VoidTaskPayload):
        f(payload)

    return test_task


endpoint_method = Mock()


@task("endpoint-test-queue", "/endpoint_test")
def cloud_task_test_endpoint(body):
    endpoint_method(body)


class CloudTaskDecoratorTest:
    def test_calling_task(self):
        inner_task = MagicMock()
        test_task = generate_task(inner_task)
        payload = {"chouquette_price": 12}

        # Synchronous call
        test_task(payload)
        # Asynchronous call, but synchronous in tests
        test_task.delay(payload)

        assert inner_task.call_args_list == [call(payload), call(payload)]

    @patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    @override_settings(IS_RUNNING_TESTS=False)
    @patch("pcapi.tasks.decorator.requests.post")
    def test_calling_task_in_dev(self, requests_post):
        inner_task = MagicMock()
        test_task = generate_task(inner_task)
        payload = {"chouquette_price": 12}

        # Synchronous call
        test_task(payload)
        requests_post.assert_not_called()

        # Asynchronous call
        test_task.delay(payload)
        requests_post.assert_called_once_with(
            "http://localhost:5000/cloud-tasks/void_task",
            headers={"HTTP_X_CLOUDTASKS_QUEUENAME": "test-queue", "AUTHORIZATION": "Bearer secret-token"},
            json={"chouquette_price": 12},
        )

    @patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    @override_settings(IS_RUNNING_TESTS=False)
    @override_settings(IS_DEV=False)
    @patch("pcapi.tasks.cloud_task.tasks_v2.CloudTasksClient")
    def test_calling_google_cloud_task_client(self, mock_tasks_client):
        inner_task = MagicMock()
        test_task = generate_task(inner_task)
        payload = {"chouquette_price": 12}

        test_task.delay(payload)

        mock_tasks_client().create_task.assert_called_once()

        _, call_args = mock_tasks_client().create_task.call_args

        assert call_args["request"]["task"]["http_request"] == {
            "body": b'{"chouquette_price": 12}',
            "headers": {"AUTHORIZATION": "Bearer " "secret-token", "Content-type": "application/json"},
            "http_method": tasks_v2.HttpMethod.POST,
            "url": f"{settings.API_URL}/cloud-tasks/void_task",
        }

    @patch("pcapi.tasks.decorator.cloud_task_api.route")
    def test_creates_a_handler_endoint(self, route_helper, app):
        route_wrapper = MagicMock()
        route_helper.return_value = route_wrapper

        inner_task = MagicMock()
        generate_task(inner_task)

        route_helper.assert_called_once_with("/void_task", methods=["POST"], endpoint="/void_task")

        route_function = route_wrapper.call_args_list[0].args[0]

        with pytest.raises(ApiErrors) as e:
            route_function({})
        assert e.value.errors["chouquette_price"] == ["Ce champ est obligatoire"]

    @patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    def test_authorization(self, client: TestClient):
        endpoint_method.reset_mock()

        response = client.post("/cloud-tasks/endpoint_test", headers={"AUTHORIZATION": "Bearer secret-token"})

        assert response.status_code == 204
        endpoint_method.assert_called_once()

    def test_unauthorized(self, client: TestClient):
        endpoint_method.reset_mock()

        response = client.post("/cloud-tasks/endpoint_test", headers={"AUTHORIZATION": "Bearer wrong-token"})

        assert response.status_code == 299
        endpoint_method.assert_not_called()
