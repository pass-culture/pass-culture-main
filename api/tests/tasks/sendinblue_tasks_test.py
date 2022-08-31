from unittest.mock import patch

from pcapi import settings
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


class SendinblueTasksTest:
    @patch("sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email")
    def test_send_transactional_email_primary_task(self, mock_send_transac_email, client):
        response = client.post(
            f"{settings.API_URL}/cloud-tasks/sendinblue/send-transactional-email-primary",
            json={
                "recipients": ["general-kenobi@coruscant.com"],
                "params": {"IMPORTANT_DATA_FOR_TEMPLATE": "Hello there"},
                "template_id": 1,
                "tags": [],
                "sender": {"email": "support@example.com", "name": "pass Culture"},
                "reply_to": {"email": "support@example.com", "name": "pass Culture"},
            },
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert len(mock_send_transac_email.call_args_list) == 1
        assert mock_send_transac_email.call_args_list[0][0][0].params == {"IMPORTANT_DATA_FOR_TEMPLATE": "Hello there"}
        assert mock_send_transac_email.call_args_list[0][0][0].tags == None
        assert mock_send_transac_email.call_args_list[0][0][0].template_id == 1
        assert mock_send_transac_email.call_args_list[0][0][0].to == [{"email": "general-kenobi@coruscant.com"}]
        assert mock_send_transac_email.call_args_list[0][0][0].sender == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args_list[0][0][0].reply_to == {
            "email": "support@example.com",
            "name": "pass Culture",
        }

    @patch("sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email")
    def test_send_transactional_email_secondary_task(self, mock_send_transac_email, client):
        response = client.post(
            f"{settings.API_URL}/cloud-tasks/sendinblue/send-transactional-email-secondary",
            json={
                "recipients": ["general-kenobi@coruscant.com"],
                "params": {"IMPORTANT_DATA_FOR_TEMPLATE": "Hello there"},
                "template_id": 1,
                "tags": [],
                "sender": {"email": "support@example.com", "name": "pass Culture"},
                "reply_to": {"email": "support@example.com", "name": "pass Culture"},
            },
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert len(mock_send_transac_email.call_args_list) == 1
        assert mock_send_transac_email.call_args_list[0][0][0].params == {"IMPORTANT_DATA_FOR_TEMPLATE": "Hello there"}
        assert mock_send_transac_email.call_args_list[0][0][0].tags == None
        assert mock_send_transac_email.call_args_list[0][0][0].template_id == 1
        assert mock_send_transac_email.call_args_list[0][0][0].to == [{"email": "general-kenobi@coruscant.com"}]
        assert mock_send_transac_email.call_args_list[0][0][0].sender == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args_list[0][0][0].reply_to == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
