from unittest.mock import patch

from sib_api_v3_sdk.rest import ApiException

from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest


class BeneficiaryTransactionalEmailsTest:
    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email",
        side_effect=ApiException(),
    )
    def test_send_transactional_email_expect_api_error(self, caplog):
        payload = SendTransactionalEmailRequest(recipients=[], template_id=1, params={}, tags=[])
        assert not send_transactional_email(payload)
        assert caplog.messages[0].startswith("Exception when calling SMTPApi->send_transac_email:")

    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email"
    )
    def test_send_transactional_email_success(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"name": "Avery"},
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        print(mock_send_transac_email.call_args)
        print(mock_send_transac_email.call_args[0])
        assert mock_send_transac_email.call_args[0][0].sender == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args[0][0].params == {"name": "Avery"}
        assert mock_send_transac_email.call_args[0][0].template_id == TransactionalEmail.EMAIL_CONFIRMATION.value.id
        assert mock_send_transac_email.call_args[0][0].to == [{"email": "avery.kelly@woobmail.com"}]
        assert mock_send_transac_email.call_args[0][0].tags == None
