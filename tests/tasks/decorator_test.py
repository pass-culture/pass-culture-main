from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

from pydantic import BaseModel
import pytest

from pcapi.core.testing import override_settings
from pcapi.models import ApiErrors
from pcapi.tasks.decorator import task


def generate_task(f):
    TEST_QUEUE = "test-queue"

    class VoidTaskPayload(BaseModel):
        chouquette_price: int

    @task(TEST_QUEUE, "/void_task")
    def test_task(payload: VoidTaskPayload):
        f(payload)

    return test_task


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

    @override_settings(IS_RUNNING_TESTS=False)
    @override_settings(IS_TESTING=True)
    @patch("pcapi.tasks.decorator.requests.post")
    def test_calling_task_in_testing(self, requests_post):
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
            headers={"HTTP_X_CLOUDTASKS_QUEUENAME": "test-queue"},
            json={"chouquette_price": 12},
        )

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
