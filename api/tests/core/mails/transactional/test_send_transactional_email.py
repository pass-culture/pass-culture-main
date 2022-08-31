import dataclasses
from unittest.mock import patch

import pytest
from sib_api_v3_sdk.rest import ApiException

from pcapi.core.mails import models
from pcapi.core.mails.transactional.send_transactional_email import send_transactional_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_address_change_confirmation import send_email_confirmation_email
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.utils import requests


class TransactionalEmailWithTemplateTest:
    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email",
        side_effect=ApiException(status=400, reason="Bad Request"),
    )
    def test_bad_request(self, mock, caplog):
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

    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email",
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

    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email"
    )
    def test_send_transactional_email_with_template_id_success(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"name": "Avery"},
            reply_to={"email": "support@example.com", "name": "pass Culture"},
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

    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email"
    )
    def test_send_transactional_email_with_reply_to_success(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            sender={"email": "support@example.com", "name": "pass Culture"},
            recipients=["avery.kelly@woobmail.com"],
            template_id=TransactionalEmail.EMAIL_CONFIRMATION.value.id,
            params={"name": "Avery"},
            reply_to={"email": "reply@example.com", "name": "reply"},
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

    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email"
    )
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

    @override_settings(EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_primary_task.delay")
    def test_to_dev_send_email_confirmation_email(self, mock_send_transactional_email_task, db_session):
        user = users_factories.UserFactory(email="john.stiles@gmail.com")
        token = users_factories.EmailValidationToken.build(user=user)
        send_email_confirmation_email(user, token=token)
        mock_send_transactional_email_task.assert_called_once()


class TransactionalEmailWithoutTemplateTest:

    data = models.SendinblueTransactionalWithoutTemplateEmailData(
        subject="test",
        html_content="contenu test",
        sender=models.SendinblueTransactionalSender.SUPPORT,
        reply_to=None,
    )

    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email"
    )
    def test_send_transactional_email_success(self, mock_send_transac_email):
        payload = SendTransactionalEmailRequest(
            sender=dataclasses.asdict(self.data.sender.value),
            recipients=["avery.kelly@woobmail.com"],
            subject="Bienvenue au pass Culture",
            html_content="Bonjour",
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
        assert mock_send_transac_email.call_args[0][0].tags is None
        assert mock_send_transac_email.call_args[0][0].reply_to == {
            "email": "support@example.com",
            "name": "pass Culture",
        }

    @patch(
        "pcapi.core.mails.transactional.send_transactional_email.sib_api_v3_sdk.api.TransactionalEmailsApi.send_transac_email"
    )
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
