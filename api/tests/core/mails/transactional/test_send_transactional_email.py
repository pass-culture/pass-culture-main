import dataclasses
from unittest.mock import patch

import brevo
import pytest
from brevo.core import ApiError as BrevoApiError

import pcapi.core.users.constants as users_constants
import pcapi.core.users.factories as users_factories
from pcapi.core import token as token_utils
from pcapi.core.mails import models
from pcapi.core.mails import serialization
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.core.mails.transactional.users.email_address_change_confirmation import send_email_confirmation_email
from pcapi.utils import requests


class TransactionalEmailWithTemplateTest:
    @patch("brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email")
    def test_bad_request(self, mock, caplog):
        mock.side_effect = BrevoApiError(
            status_code=400,
            headers={"Content-Type": "application/json"},
            body={"code": "test_code", "message": "test_message"},
        )

        payload = serialization.SendTransactionalEmailRequest(
            recipients=[], params={}, template_id=1, tags=[], sender={}, reply_to={}
        )

        with pytest.raises(requests.ExternalAPIException) as exception_info:
            send_transactional_email(payload)

        assert exception_info.value.is_retryable is False
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].message == "Exception when calling Brevo send_transac_email"
        assert caplog.records[0].extra == {
            "payload": {
                "attachment": None,
                "bcc_recipients": [],
                "enable_unsubscribe": False,
                "html_content": None,
                "params": {},
                "recipients": [],
                "reply_to": {},
                "sender": {},
                "subject": None,
                "tags": [],
                "template_id": 1,
                "use_pro_subaccount": False,
            },
            "status_code": 400,
            "body": {"code": "test_code", "message": "test_message"},
        }
        assert len(caplog.records) == 1

    @patch("brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email")
    def test_error_not_json(self, mock, caplog):
        mock.side_effect = BrevoApiError(
            status_code=400,
            headers={"Content-Type": "application/json"},
            body="This is an error message",
        )

        payload = serialization.SendTransactionalEmailRequest(
            recipients=[], params={}, template_id=1, tags=[], sender={}, reply_to={}
        )

        with pytest.raises(requests.ExternalAPIException) as exception_info:
            send_transactional_email(payload)

        assert exception_info.value.is_retryable is False
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].message == "Exception when calling Brevo send_transac_email"
        assert caplog.records[0].extra == {
            "payload": {
                "attachment": None,
                "bcc_recipients": [],
                "enable_unsubscribe": False,
                "html_content": None,
                "params": {},
                "recipients": [],
                "reply_to": {},
                "sender": {},
                "subject": None,
                "tags": [],
                "template_id": 1,
                "use_pro_subaccount": False,
            },
            "status_code": 400,
            "body": "This is an error message",
        }
        assert len(caplog.records) == 1

    @patch("brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email")
    def test_email_not_valid(self, mock, caplog):
        mock.side_effect = BrevoApiError(
            status_code=400,
            headers={"Content-Type": "application/json"},
            body={"code": "invalid_parameter", "message": "email is not valid in to"},
        )

        payload = serialization.SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["invalid@example", "other@example.com"],
            bcc_recipients=["bcc@example.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"NAME": "Avery"},
            reply_to={"email": "support@example.com", "name": "pass Culture"},
            enable_unsubscribe=False,
        )

        send_transactional_email(payload)

        assert caplog.records[0].levelname == "ERROR"
        assert (
            caplog.records[0].message
            == "Brevo can't send email to inv***@example,oth***@example.com: code=invalid_parameter, message=email is not valid in to"
        )
        assert caplog.records[0].extra == {
            "payload": {
                "attachment": None,
                "bcc_recipients": ["bcc@example.com"],
                "enable_unsubscribe": False,
                "html_content": None,
                "params": {"NAME": "Avery"},
                "recipients": ["invalid@example", "other@example.com"],
                "reply_to": {"email": "support@example.com", "name": "pass Culture"},
                "sender": {"email": "support@example.com", "name": "pass Culture"},
                "subject": None,
                "tags": None,
                "template_id": TransactionalEmail.EMAIL_CONFIRMATION.value.id,
                "use_pro_subaccount": False,
            },
            "status_code": 400,
            "body": {"code": "invalid_parameter", "message": "email is not valid in to"},
        }
        assert len(caplog.records) == 1

    @patch(
        "brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email",
        side_effect=BrevoApiError(status_code=524, body="Bad Request"),
    )
    def test_external_api_unavailable(self, mock, caplog):
        payload = serialization.SendTransactionalEmailRequest(
            recipients=[], params={}, template_id=1, tags=[], sender={}, reply_to={}
        )

        with pytest.raises(requests.ExternalAPIException) as exception_info:
            send_transactional_email(payload)

        assert exception_info.value.is_retryable is True
        assert isinstance(exception_info.value.__cause__, BrevoApiError)

        assert len(caplog.records) == 0

    @patch("brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email")
    def test_send_transactional_email_with_template_id_success(self, mock_send_transac_email):
        payload = serialization.SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"NAME": "Avery"},
            reply_to={"email": "support@example.com", "name": "pass Culture"},
            enable_unsubscribe=False,
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        assert mock_send_transac_email.call_args.kwargs == {
            "sender": brevo.SendTransacEmailRequestSender(email="support@example.com", name="pass Culture"),
            "params": {"NAME": "Avery"},
            "template_id": TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            "to": [brevo.SendTransacEmailRequestToItem(email="avery.kelly@woobmail.com", name=None)],
            "reply_to": brevo.SendTransacEmailRequestReplyTo(email="support@example.com", name="pass Culture"),
            "headers": {"X-List-Unsub": "disabled"},
        }

    @patch("brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email")
    def test_send_transactional_email_with_reply_to_success(self, mock_send_transac_email):
        payload = serialization.SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"NAME": "Avery"},
            reply_to={"email": "reply@example.com", "name": "reply"},
            enable_unsubscribe=True,
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        assert mock_send_transac_email.call_args.kwargs == {
            "sender": brevo.SendTransacEmailRequestSender(email="support@example.com", name="pass Culture"),
            "params": {"NAME": "Avery"},
            "template_id": TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            "to": [brevo.SendTransacEmailRequestToItem(email="avery.kelly@woobmail.com", name=None)],
            "reply_to": brevo.SendTransacEmailRequestReplyTo(email="reply@example.com", name="reply"),
        }

    @patch("brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email")
    def test_send_transactional_email_with_template_id_success_empty_params(self, mock_send_transac_email):
        payload = serialization.SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={},
            reply_to={"email": "support@example.com", "name": "pass Culture"},
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        assert mock_send_transac_email.call_args.kwargs == {
            "sender": brevo.SendTransacEmailRequestSender(email="support@example.com", name="pass Culture"),
            "template_id": TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            "to": [brevo.SendTransacEmailRequestToItem(email="avery.kelly@woobmail.com", name=None)],
            "reply_to": brevo.SendTransacEmailRequestReplyTo(email="support@example.com", name="pass Culture"),
            "headers": {"X-List-Unsub": "disabled"},
        }

    @pytest.mark.settings(EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @patch("pcapi.core.mails.tasks.send_transactional_email_primary_task.delay")
    def test_to_dev_send_email_confirmation_email(self, mock_send_transactional_email_task, db_session):
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

    @patch("brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email")
    def test_send_transactional_email_success(self, mock_send_transac_email):
        payload = serialization.SendTransactionalEmailRequest(
            sender=dataclasses.asdict(self.data.sender.value),
            recipients=["avery.kelly@woobmail.com"],
            subject="Bienvenue au pass Culture",
            html_content="Bonjour",
            reply_to=dataclasses.asdict(self.data.reply_to),
            enable_unsubscribe=False,
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        assert mock_send_transac_email.call_args.kwargs == {
            "sender": brevo.SendTransacEmailRequestSender(email="support@example.com", name="pass Culture"),
            "subject": "Bienvenue au pass Culture",
            "html_content": "Bonjour",
            "to": [brevo.SendTransacEmailRequestToItem(email="avery.kelly@woobmail.com", name=None)],
            "reply_to": brevo.SendTransacEmailRequestReplyTo(email="support@example.com", name="pass Culture"),
            "headers": {"X-List-Unsub": "disabled"},
        }

    @patch("brevo.transactional_emails.client.TransactionalEmailsClient.send_transac_email")
    def test_send_transactional_email_success_empty_attachement(self, mock_send_transac_email):
        payload = serialization.SendTransactionalEmailRequest(
            sender=dataclasses.asdict(self.data.sender.value),
            recipients=["avery.kelly@woobmail.com"],
            subject="Bienvenue au pass Culture",
            html_content="Bonjour",
            attachment=None,
            reply_to=dataclasses.asdict(self.data.reply_to),
        )
        send_transactional_email(payload)

        mock_send_transac_email.assert_called_once()
        assert mock_send_transac_email.call_args.kwargs == {
            "sender": brevo.SendTransacEmailRequestSender(email="support@example.com", name="pass Culture"),
            "subject": "Bienvenue au pass Culture",
            "html_content": "Bonjour",
            "to": [brevo.SendTransacEmailRequestToItem(email="avery.kelly@woobmail.com", name=None)],
            "reply_to": brevo.SendTransacEmailRequestReplyTo(email="support@example.com", name="pass Culture"),
            "headers": {"X-List-Unsub": "disabled"},
        }
