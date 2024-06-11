from unittest import mock

from google.cloud import tasks_v2

from pcapi import settings
from pcapi.core.testing import override_settings
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task
from pcapi.utils import requests

from tests.conftest import TestClient


slow_chouquette_handler = mock.Mock()


class ChouquetteSender(BaseModel):
    number: int


@task("chouquettes-test-queue", "/send-chouquettes")
def send_chouquettes(payload: ChouquetteSender):
    slow_chouquette_handler(payload.number)


class CloudTaskDecoratorTest:
    def teardown_method(self, method):
        slow_chouquette_handler.reset_mock()

    def test_calling_function_in_tests(self):
        # When running tests, the decorated function is executed
        # immediately, whether or not we use `.delay()`.
        payload = ChouquetteSender(number=12)

        send_chouquettes(payload)
        send_chouquettes.delay(payload)

        assert slow_chouquette_handler.call_args_list == [mock.call(12), mock.call(12)]

    @override_settings(IS_RUNNING_TESTS=False, IS_REBUILD_STAGING=True)
    @mock.patch("pcapi.tasks.cloud_task.requests.post")
    def test_rebuild_staging_does_not_create_cloud_task(self, requests_post):
        # When rebuilding staging, we do not call any cloud_task
        payload = ChouquetteSender(number=12)

        send_chouquettes(payload)
        send_chouquettes.delay(payload)

        requests_post.assert_not_called()
        assert slow_chouquette_handler.call_args_list == [mock.call(12), mock.call(12)]

    @mock.patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    @override_settings(IS_RUNNING_TESTS=False, IS_DEV=True)
    @mock.patch("pcapi.tasks.cloud_task.requests.post")
    def test_calling_function_in_development_environment(self, requests_post):
        # When running locally ("development" environment), the
        # decorated function is not directly executed, but our code
        # calls our own route (to simulate Google Cloud Tasks calling
        # that route).
        payload = ChouquetteSender(number=12)

        # Synchronous call.
        send_chouquettes(payload)
        slow_chouquette_handler.assert_called_with(12)
        requests_post.assert_not_called()
        slow_chouquette_handler.reset_mock()

        # "Asynchronous" (more or less) call. Our code calls our own
        # route.
        send_chouquettes.delay(payload)
        slow_chouquette_handler.assert_not_called()
        requests_post.assert_called_once_with(
            f"{settings.API_URL}/cloud-tasks/send-chouquettes",
            headers={
                "HTTP_X_CLOUDTASKS_QUEUENAME": "chouquettes-test-queue",
                "AUTHORIZATION": "Bearer secret-token",
            },
            json={"number": 12},
        )

    @mock.patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    @override_settings(IS_RUNNING_TESTS=False, CLOUD_TASK_CALL_INTERNAL_API_ENDPOINT=False)
    def test_calling_function_calls_google_cloud_tasks(self, cloud_task_client):
        # When running in production, the decorated function is not
        # directly executed. Instead, we call Google Cloud Tasks and
        # ask it to call our task route.
        cloud_task_client.queue_path.return_value = "fake queue path"

        payload = ChouquetteSender(number=12)
        send_chouquettes.delay(payload)

        slow_chouquette_handler.assert_not_called()
        cloud_task_client.create_task.assert_called_once()
        _, call_args = cloud_task_client.create_task.call_args
        assert call_args["request"] == tasks_v2.CreateTaskRequest(
            parent="fake queue path",
            task=tasks_v2.Task(
                http_request=tasks_v2.HttpRequest(
                    body=b'{"number": 12}',
                    headers={
                        "AUTHORIZATION": "Bearer " "secret-token",
                        "Content-type": "application/json",
                    },
                    http_method=tasks_v2.HttpMethod.POST,
                    url=f"{settings.API_URL}/cloud-tasks/send-chouquettes",
                )
            ),
        )

    @mock.patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    def test_route_ok(self, client):
        # When using the `task` decorator, a route is defined and can
        # be used.
        response = client.post(
            "/cloud-tasks/send-chouquettes",
            headers={"AUTHORIZATION": "Bearer secret-token"},
            json={"number": 12},
        )
        assert response.status_code == 204
        slow_chouquette_handler.assert_called_once_with(12)

    @mock.patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    def test_route_invalid_input(self, client):
        # When using the `task` decorator, a route is defined and
        # validates input.
        response = client.post(
            "/cloud-tasks/send-chouquettes",
            headers={"AUTHORIZATION": "Bearer secret-token"},
            json={"number": "not a number"},
        )
        assert response.status_code == 400
        assert response.json == {"number": ["Saisissez un nombre valide"]}

    def test_route_unauthorized(self, client):
        # When using the `task` decorator, a route is defined and
        # verifies authorization.
        response = client.post(
            "/cloud-tasks/send-chouquettes",
            headers={"AUTHORIZATION": "Bearer wrong-token"},
            json={"number": 12},
        )
        assert response.status_code == 299


class PostHandlerTest:
    def teardown_method(self, method):
        slow_chouquette_handler.reset_mock()

    @mock.patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    def test_max_attempt_reached(self, client: TestClient, caplog):
        slow_chouquette_handler.side_effect = requests.ExternalAPIException(is_retryable=True)

        response = client.post(
            "/cloud-tasks/send-chouquettes",
            headers={
                "AUTHORIZATION": "Bearer secret-token",
                "X-CloudTasks-TaskRetryCount": "9",
            },
            json={"number": 12},
        )

        assert response.status_code == 400
        assert len(caplog.records) == 1
        assert caplog.records[0].message == "External API unavailable for CloudTask /send-chouquettes"
        assert caplog.records[0].levelname == "ERROR"

    @mock.patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    def test_max_attempt_not_reached(self, client: TestClient, caplog):
        slow_chouquette_handler.side_effect = requests.ExternalAPIException(is_retryable=True)

        response = client.post(
            "/cloud-tasks/send-chouquettes",
            headers={"AUTHORIZATION": "Bearer secret-token", "X-CloudTasks-TaskRetryCount": "8"},
            json={"number": 12},
        )

        assert response.status_code == 400
        assert len(caplog.records) == 1
        assert (
            caplog.records[0].message
            == "The cloud task has failed and will automatically be retried: /send-chouquettes"
        )
        assert caplog.records[0].levelname == "WARNING"

    @mock.patch("pcapi.tasks.cloud_task.AUTHORIZATION_HEADER_VALUE", "Bearer secret-token")
    def test_not_retryable(self, client: TestClient):
        slow_chouquette_handler.side_effect = requests.ExternalAPIException(is_retryable=False)

        response = client.post(
            "/cloud-tasks/send-chouquettes",
            headers={
                "AUTHORIZATION": "Bearer secret-token",
                "X-CloudTasks-TaskRetryCount": "8",
            },
            json={"number": 12},
        )

        assert response.status_code == 204
