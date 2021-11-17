from google.cloud import tasks_v2
import requests_mock

from pcapi.core.testing import override_settings
from pcapi.core.users.external.batch import format_user_attributes
from pcapi.notifications.push.backends.batch import BatchBackend
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationMessage

from tests.core.users.external import common_user_attributes


class BatchPushNotificationClientTest:
    @override_settings(BATCH_SECRET_API_KEY="coucou-la-cle")
    def test_update_user_attributes(self, cloud_task_client):
        BatchBackend().update_user_attributes(1, {"attri": "but"})

        assert cloud_task_client.create_task.call_count == 2

        ((_, ios_call_args), (_, android_call_args)) = cloud_task_client.create_task.call_args_list

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

    @override_settings(BATCH_SECRET_API_KEY="coucou-la-cle")
    def test_update_user_attributes_complete_data(self, cloud_task_client):
        attributes = format_user_attributes(common_user_attributes)
        BatchBackend().update_user_attributes(1, attributes)

        assert cloud_task_client.create_task.call_count == 2

        ((_, ios_call_args), (_, android_call_args)) = cloud_task_client.create_task.call_args_list

        body_bytestr = (
            b'{"overwrite": false, '
            b'"values": {'
            b'"u.credit": 48000, '
            b'"u.departement_code": "12", '
            b'"date(u.date_of_birth)": "2003-05-06T00:00:00", '
            b'"u.postal_code": null, '
            b'"date(u.date_created)": "2021-02-06T00:00:00", '
            b'"u.marketing_push_subscription": true, '
            b'"u.is_beneficiary": true, '
            b'"date(u.deposit_expiration_date)": null, '
            b'"date(u.last_booking_date)": "2021-05-06T00:00:00", '
            b'"ut.roles": ["BENEFICIARY"], '
            b'"date(u.product_brut_x_use)": "2021-05-06T00:00:00", '
            b'"ut.booking_categories": ["CINEMA", "LIVRE"]'
            b"}}"
        )

        assert ios_call_args["request"]["task"]["http_request"] == {
            "body": body_bytestr,
            "headers": {"Content-Type": "application/json", "X-Authorization": "coucou-la-cle"},
            "http_method": tasks_v2.HttpMethod.POST,
            "url": "https://api.example.com/1.0/fake_android_api_key/data/users/1",
        }

        assert android_call_args["request"]["task"]["http_request"] == {
            "body": body_bytestr,
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
