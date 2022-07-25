import requests_mock

from pcapi import settings
from pcapi.core.testing import override_settings
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


@override_settings(PUSH_NOTIFICATION_BACKEND="pcapi.notifications.push.backends.batch.BatchBackend")
def test_batch_task_ios(client):
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://api.batch.com/1.0/fake_ios_api_key/data/users/123")
        response = client.post(
            f"{settings.API_URL}/cloud-tasks/batch/ios/update_user_attributes",
            json={"user_id": 123, "attributes": {"TEXTE_À": True}},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )
        assert response.status_code == 204
        posted_json = posted.last_request.json()

    assert posted_json == {"overwrite": False, "values": {"TEXTE_À": True}}


@override_settings(PUSH_NOTIFICATION_BACKEND="pcapi.notifications.push.backends.batch.BatchBackend")
def test_batch_task_android(client):
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://api.batch.com/1.0/fake_android_api_key/data/users/123")
        response = client.post(
            f"{settings.API_URL}/cloud-tasks/batch/android/update_user_attributes",
            json={"user_id": 123, "attributes": {"TEXTE_À": True}},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )
        assert response.status_code == 204
        posted_json = posted.last_request.json()

    assert posted_json == {"overwrite": False, "values": {"TEXTE_À": True}}


@override_settings(PUSH_NOTIFICATION_BACKEND="pcapi.notifications.push.backends.batch.BatchBackend")
def test_batch_task_retry(client, caplog):
    with requests_mock.Mocker() as mock:
        mock.post(
            "https://api.batch.com/1.0/fake_android_api_key/data/users/123",
            exc=ValueError,
        )
        response = client.post(
            f"{settings.API_URL}/cloud-tasks/batch/android/update_user_attributes",
            json={"user_id": 123, "attributes": {"TEXTE_À": True}},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )
        assert response.status_code == 400
    assert caplog.records[1].levelname == "WARNING"
    assert caplog.records[1].message == "Exception with Batch update_user_attributes API"


@override_settings(PUSH_NOTIFICATION_BACKEND="pcapi.notifications.push.backends.batch.BatchBackend")
def test_batch_bad_request_must_not_be_retried(caplog, client):
    with requests_mock.Mocker() as mock:
        mock.post("https://api.batch.com/1.0/fake_android_api_key/data/users/123", status_code=400)
        response = client.post(
            f"{settings.API_URL}/cloud-tasks/batch/android/update_user_attributes",
            json={"user_id": 123, "attributes": {"TEXTE_À": True}},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "Error with Batch update_user_attributes API: 400"
    assert response.status_code == 204
