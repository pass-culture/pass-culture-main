import dataclasses
from unittest.mock import patch

from brevo_python.rest import ApiException
import pytest
from urllib3.response import HTTPResponse

from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_address_change_confirmation import send_email_confirmation_email
import pcapi.core.users.constants as users_constants
import pcapi.core.users.factories as users_factories
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.utils import requests


class TransactionalEmailWithTemplateTest:
    @patch("brevo_python.api.TransactionalEmailsApi.send_transac_email")
    def test_bad_request(self, mock, caplog):
        mock.side_effect = ApiException(
            http_resp=HTTPResponse(
                status=400,
                reason="Bad Request",
                headers={"Content-Type": "application/json"},
                body='{"code":"test_code","message":"test_message"}',
            )
        )

        payload = SendTransactionalEmailRequest(
            recipients=[], params={}, template_id=1, tags=[], sender={}, reply_to={}
        )

        with pytest.raises(requests.ExternalAPIException) as exception_info:
            send_transactional_email(payload)

        assert exception_info.value.is_retryable is False
        assert caplog.records[0].levelname == "ERROR"
        assert (
            caplog.records[0].message
            == "Exception when calling Sendinblue send_transac_email with status=400 and code=test_code"
        )
        assert len(caplog.records) == 1

    @patch("brevo_python.api.TransactionalEmailsApi.send_transac_email")
    def test_error_not_json(self, mock, caplog):
        mock.side_effect = ApiException(
            http_resp=HTTPResponse(
                status=400,
                reason="Bad Request",
                headers={"Content-Type": "application/json"},
                body="This is an error message",
            )
        )

        payload = SendTransactionalEmailRequest(
            recipients=[], params={}, template_id=1, tags=[], sender={}, reply_to={}
        )

        with pytest.raises(requests.ExternalAPIException) as exception_info:
            send_transactional_email(payload)

        assert exception_info.value.is_retryable is False
        assert caplog.records[0].levelname == "ERROR"
        assert (
            caplog.records[0].message
            == "Exception when calling Sendinblue send_transac_email with status=400 and code=unknown"
        )
        assert len(caplog.records) == 1

    @patch("brevo_python.api.TransactionalEmailsApi.send_transac_email")
    def test_email_not_valid(self, mock, caplog):
        mock.side_effect = ApiException(
            http_resp=HTTPResponse(
                status=400,
                reason="Bad Request",
                headers={"Content-Type": "application/json"},
                body='{"code":"invalid_parameter","message":"email is not valid in to"}',
            )
        )

        payload = SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["invalid@example", "other@example.com"],
            bcc_recipients=["bcc@example.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"name": "Avery"},
            reply_to={"email": "support@example.com", "name": "pass Culture"},
            enable_unsubscribe=False,
        )

        send_transactional_email(payload)

        assert caplog.records[0].levelname == "ERROR"
        assert (
            caplog.records[0].message
            == "Sendinblue can't send email to inv***@example,oth***@example.com: code=invalid_parameter, message=email is not valid in to"
        )
        assert caplog.records[0].extra == {
            "template_id": TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            "recipients": ["invalid@example", "other@example.com"],
            "bcc_recipients": ["bcc@example.com"],
        }
        assert len(caplog.records) == 1

    @patch(
        "brevo_python.api.TransactionalEmailsApi.send_transac_email",
        side_effect=ApiException(status=524, reason="Bad Request"),
    )
    def test_external_api_unavailable(self, mock, caplog):
        payload = SendTransactionalEmailRequest(
            recipients=[], params={}, template_id=1, tags=[], sender={}, reply_to={}
        )

        with pytest.raises(requests.ExternalAPIException) as exception_info:
            send_transactional_email(payload)

        assert exception_info.value.is_retryable is True
        assert isinstance(exception_info.value.__cause__, ApiException)

        assert len(caplog.records) == 0

    @patch("brevo_python.api.TransactionalEmailsApi.send_transac_email")
    def test_send_transactional_email_with_template_id_success(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"name": "Avery"},
            reply_to={"email": "support@example.com", "name": "pass Culture"},
            enable_unsubscribe=False,
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
        assert mock_send_transac_email.call_args[0][0].tags is None
        assert mock_send_transac_email.call_args[0][0].reply_to == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args[0][0].headers == {"X-List-Unsub": "disabled"}

    @patch("brevo_python.api.TransactionalEmailsApi.send_transac_email")
    def test_send_transactional_email_with_reply_to_success(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"name": "Avery"},
            reply_to={"email": "reply@example.com", "name": "reply"},
            enable_unsubscribe=True,
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
        assert mock_send_transac_email.call_args[0][0].tags is None
        assert mock_send_transac_email.call_args[0][0].reply_to == {"email": "reply@example.com", "name": "reply"}
        assert mock_send_transac_email.call_args[0][0].headers is None

    @patch("brevo_python.api.TransactionalEmailsApi.send_transac_email")
    def test_send_transactional_email_with_template_id_success_empty_params(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={},
            reply_to={"email": "support@example.com", "name": "pass Culture"},
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        assert mock_send_transac_email.call_args[0][0].sender == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args[0][0].params is None
        assert mock_send_transac_email.call_args[0][0].template_id == TransactionalEmail.EMAIL_CONFIRMATION.value.id
        assert mock_send_transac_email.call_args[0][0].to == [{"email": "avery.kelly@woobmail.com"}]
        assert mock_send_transac_email.call_args[0][0].tags is None
        assert mock_send_transac_email.call_args[0][0].reply_to == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args[0][0].headers == {"X-List-Unsub": "disabled"}

    @pytest.mark.settings(EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_primary_task_cloud_tasks.delay")
    def test_to_dev_send_email_confirmation_email(self, mock_send_transactional_email_task, db_session):
        user = users_factories.UserFactory(email="john.stiles@gmail.com")
        token = token_utils.Token.create(
            type_=token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
            ttl=users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
            user_id=user.id,
        )
        send_email_confirmation_email(user.email, token=token)
        mock_send_transactional_email_task.assert_called_once()

    @pytest.mark.settings(EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @pytest.mark.features(WIP_ASYNCHRONOUS_CELERY_MAILS=True)
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_primary_task_celery.delay")
    def test_to_dev_send_email_confirmation_email_through_celery(self, mock_send_transactional_email_task, db_session):
        user = users_factories.UserFactory(email="john.celery@gmail.com")
        token = token_utils.Token.create(
            type_=token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
            ttl=users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
            user_id=user.id,
        )
        send_email_confirmation_email(user.email, token=token)
        mock_send_transactional_email_task.assert_called_once()


class TransactionalEmailWithoutTemplateTest:
    data = models.TransactionalWithoutTemplateEmailData(
        subject="test",
        html_content="contenu test",
        sender=models.TransactionalSender.SUPPORT,
        reply_to=None,
    )

    @patch("brevo_python.api.TransactionalEmailsApi.send_transac_email")
    def test_send_transactional_email_success(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            sender=dataclasses.asdict(self.data.sender.value),
            recipients=["avery.kelly@woobmail.com"],
            subject="Bienvenue au pass Culture",
            html_content="Bonjour",
            reply_to=dataclasses.asdict(self.data.reply_to),
            enable_unsubscribe=False,
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        assert mock_send_transac_email.call_args[0][0].sender == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args[0][0].subject == "Bienvenue au pass Culture"
        assert mock_send_transac_email.call_args[0][0].html_content == "Bonjour"
        assert mock_send_transac_email.call_args[0][0].to == [{"email": "avery.kelly@woobmail.com"}]
        assert mock_send_transac_email.call_args[0][0].tags is None
        assert mock_send_transac_email.call_args[0][0].reply_to == {
            "email": "support@example.com",
            "name": "pass Culture",
        }

    @patch("brevo_python.api.TransactionalEmailsApi.send_transac_email")
    def test_send_transactional_email_success_empty_attachement(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            sender=dataclasses.asdict(self.data.sender.value),
            recipients=["avery.kelly@woobmail.com"],
            subject="Bienvenue au pass Culture",
            html_content="Bonjour",
            attachment=None,
            reply_to=dataclasses.asdict(self.data.reply_to),
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        assert mock_send_transac_email.call_args[0][0].sender == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
        assert mock_send_transac_email.call_args[0][0].subject == "Bienvenue au pass Culture"
        assert mock_send_transac_email.call_args[0][0].html_content == "Bonjour"
        assert mock_send_transac_email.call_args[0][0].to == [{"email": "avery.kelly@woobmail.com"}]
        assert mock_send_transac_email.call_args[0][0].attachment is None
        assert mock_send_transac_email.call_args[0][0].reply_to == {
            "email": "support@example.com",
            "name": "pass Culture",
        }
