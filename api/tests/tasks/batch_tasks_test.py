from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.core.testing import override_settings
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


pytestmark = pytest.mark.usefixtures("db_session")


@override_settings(PUSH_NOTIFICATION_BACKEND="pcapi.notifications.push.backends.batch.BatchBackend")
@patch("pcapi.notifications.push.backends.batch.requests")
def test_legacy_batch_task(request_mock, client):
    response = client.post(
        f"{settings.API_URL}/cloud-tasks/batch/update_user_attributes",
        json={"user_id": 123, "attributes": {"TEXTE_À": True}},
        headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
    )
    assert response.status_code == 204

    ((android_url, android_call_args), (ios_url, ios_call_args)) = request_mock.post.call_args_list

    assert android_url == ("https://api.example.com/1.0/fake_android_api_key/data/users/123",)
    assert android_call_args["json"] == {"overwrite": False, "values": {"TEXTE_À": True}}

    assert ios_url == ("https://api.example.com/1.0/fake_ios_api_key/data/users/123",)
    assert ios_call_args["json"] == {"overwrite": False, "values": {"TEXTE_À": True}}
