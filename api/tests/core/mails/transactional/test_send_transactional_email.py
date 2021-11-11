from unittest.mock import patch

from sib_api_v3_sdk.rest import ApiException

from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_confirmation_email import send_email_confirmation_email
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
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
        assert mock_send_transac_email.call_args[0][0].sender == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args[0][0].params == {"name": "Avery"}
        assert mock_send_transac_email.call_args[0][0].template_id == TransactionalEmail.EMAIL_CONFIRMATION.value.id
        assert mock_send_transac_email.call_args[0][0].to == [{"email": "avery.kelly@woobmail.com"}]
        assert mock_send_transac_email.call_args[0][0].tags == None

    @override_settings(EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_task.delay")
    def test_to_dev_send_email_confirmation_email(self, mock_send_transactional_email_task, db_session):
        user = users_factories.UserFactory(email="john.stiles@gmail.com")
        token = users_factories.EmailValidationToken.build(user=user)
        send_email_confirmation_email(user, token=token)
        mock_send_transactional_email_task.assert_called_once()
