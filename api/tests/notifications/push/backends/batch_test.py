import requests_mock

from pcapi.notifications.push.backends.batch import BatchAPI
from pcapi.notifications.push.backends.batch import BatchBackend
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationMessage


class BatchPushNotificationClientTest:
    def test_update_user_attributes(self):
        with requests_mock.Mocker() as mock:
            ios_post = mock.post("https://api.example.com/1.0/fake_android_api_key/data/users/1")

            BatchBackend().update_user_attributes(BatchAPI.ANDROID, 1, {"attri": "but"})

            assert ios_post.last_request.json() == {"overwrite": False, "values": {"attri": "but"}}

    def test_send_transactional_notification(self):
        with requests_mock.Mocker() as mock:
            android_post = mock.post("https://api.example.com/1.1/fake_android_api_key/transactional/send")
            ios_post = mock.post("https://api.example.com/1.1/fake_ios_api_key/transactional/send")

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
            android_post = mock.post("https://api.example.com/1.1/fake_android_api_key/transactional/send")
            ios_post = mock.post("https://api.example.com/1.1/fake_ios_api_key/transactional/send")

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
