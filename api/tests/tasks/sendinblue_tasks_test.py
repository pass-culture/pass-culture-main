from unittest.mock import patch

from pcapi import settings
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


class SendinblueTasksTest:
    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email"
    )
    def test_send_transactional_email_task(self, mock_send_transac_email, client):
        response = client.post(
            f"{settings.API_URL}/cloud-tasks/sendinblue/send-transactional-email",
            json={
                "recipients": ["general-kenobi@coruscant.com"],
                "params": {"IMPORTANT_DATA_FOR_TEMPLATE": "Hello there"},
                "template_id": 1,
                "tags": [],
            },
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert len(mock_send_transac_email.call_args_list) == 1
        assert mock_send_transac_email.call_args_list[0][0][0].params == {"IMPORTANT_DATA_FOR_TEMPLATE": "Hello there"}
        assert mock_send_transac_email.call_args_list[0][0][0].tags == []
        assert mock_send_transac_email.call_args_list[0][0][0].template_id == 1
        assert mock_send_transac_email.call_args_list[0][0][0].to == [{"email": "general-kenobi@coruscant.com"}]
