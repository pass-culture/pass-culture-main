from unittest.mock import MagicMock
from unittest.mock import patch

from google.cloud import tasks_v2
import requests_mock

from pcapi.core.testing import override_settings
from pcapi.notifications.push.backends.batch import BatchBackend
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationMessage


class BatchPushNotificationClientTest:
    @override_settings(BATCH_SECRET_API_KEY="coucou-la-cle")
    @patch("pcapi.tasks.cloud_task.get_client")
    def test_update_user_attributes(self, mock_get_client):
        client_mock = MagicMock()
        mock_get_client.return_value = client_mock
        BatchBackend().update_user_attributes(1, {"attri": "but"})

        assert client_mock.create_task.call_count == 2

        ((_, ios_call_args), (_, android_call_args)) = client_mock.create_task.call_args_list

        assert ios_call_args["request"]["task"]["http_request"] == {
            "body": b'{"overwrite": false, "values": {"attri": "but"}}',
            "headers": {"Content-Type": "application/json", "X-Authorization": "coucou-la-cle"},
            "http_method": tasks_v2.HttpMethod.POST,
            "url": "https://api.example.com/1.0/fake_android_api_key/data/users/1",
        }

        assert android_call_args["request"]["task"]["http_request"] == {
            "body": b'{"overwrite": false, "values": {"attri": "but"}}',
            "headers": {"Content-Type": "application/json", "X-Authorization": "coucou-la-cle"},
            "http_method": tasks_v2.HttpMethod.POST,
            "url": "https://api.example.com/1.0/fake_ios_api_key/data/users/1",
        }

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
