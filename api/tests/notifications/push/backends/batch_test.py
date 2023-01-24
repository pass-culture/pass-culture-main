import requests_mock

from pcapi.notifications.push.backends.batch import BatchAPI
from pcapi.notifications.push.backends.batch import BatchBackend
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationMessage


class BatchPushNotificationClientTest:
    def test_update_user_attributes(self):
        with requests_mock.Mocker() as mock:
            ios_post = mock.post("https://api.batch.com/1.0/fake_android_api_key/data/users/1")

            BatchBackend().update_user_attributes(BatchAPI.ANDROID, 1, {"attri": "but"})

            assert ios_post.last_request.json() == {"overwrite": False, "values": {"attri": "but"}}

    def test_send_transactional_notification(self):
        with requests_mock.Mocker() as mock:
            android_post = mock.post("https://api.batch.com/1.1/fake_android_api_key/transactional/send")
            ios_post = mock.post("https://api.batch.com/1.1/fake_ios_api_key/transactional/send")

            BatchBackend().send_transactional_notification(
                TransactionalNotificationData(
                    group_id="Group_id",
                    user_ids=[1234, 4321],
                    message=TransactionalNotificationMessage(title="Putsch", body="Notif"),
                )
            )

            assert ios_post.last_request.json() == {
                "group_id": "Group_id",
                "recipients": {"custom_ids": ["1234", "4321"]},
                "message": {"body": "Notif", "title": "Putsch"},
            }
            assert android_post.last_request.json() == {
                "group_id": "Group_id",
                "recipients": {"custom_ids": ["1234", "4321"]},
                "message": {"body": "Notif", "title": "Putsch"},
            }

    def test_api_exception(self):
        with requests_mock.Mocker() as mock:
            android_post = mock.post("https://api.batch.com/1.1/fake_android_api_key/transactional/send")
            ios_post = mock.post("https://api.batch.com/1.1/fake_ios_api_key/transactional/send")

            BatchBackend().send_transactional_notification(
                TransactionalNotificationData(
                    group_id="Group_id",
                    user_ids=[1234, 4321],
                    message=TransactionalNotificationMessage(title="Putsch", body="Notif"),
                )
            )

            assert ios_post.last_request.json() == {
                "group_id": "Group_id",
                "recipients": {"custom_ids": ["1234", "4321"]},
                "message": {"body": "Notif", "title": "Putsch"},
            }
            assert android_post.last_request.json() == {
                "group_id": "Group_id",
                "recipients": {"custom_ids": ["1234", "4321"]},
                "message": {"body": "Notif", "title": "Putsch"},
            }

    def test_send_user_events(self):
        with requests_mock.Mocker() as mock:
            android_post = mock.post("https://api.batch.com/1.0/fake_android_api_key/events/users/")
            ios_post = mock.post("https://api.batch.com/1.0/fake_ios_api_key/events/users/")

            BatchBackend().track_event_for_multiple_users(
                user_ids=[1, 22, 88], event_name="taylor_trigger", event_payload={"location": "Brockton Bay"}
            )

            expected_request_body = [
                {"id": 1, "events": [{"name": "ue.taylor_trigger", "attributes": {"location": "Brockton Bay"}}]},
                {"id": 22, "events": [{"name": "ue.taylor_trigger", "attributes": {"location": "Brockton Bay"}}]},
                {"id": 88, "events": [{"name": "ue.taylor_trigger", "attributes": {"location": "Brockton Bay"}}]},
            ]

            assert ios_post.last_request.json() == expected_request_body
            assert android_post.last_request.json() == expected_request_body
