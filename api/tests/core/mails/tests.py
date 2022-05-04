import copy
import dataclasses
from unittest.mock import patch

import pytest
import requests.exceptions
import requests_mock

from pcapi.core import mails
import pcapi.core.mails.backends.mailjet
from pcapi.core.mails.models import sendinblue_models
from pcapi.core.mails.models.models import Email
from pcapi.core.mails.models.models import EmailStatus
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.tasks.serialization import sendinblue_tasks


@pytest.mark.usefixtures("db_session")
class SendTest:

    recipients = ["recipient1@example.com", "recipient2@example.com"]
    data = {"key": "value", "Vars": {"other-key": "other-value"}}
    expected_sent_data = {
        "FromEmail": "support@example.com",
        "To": ", ".join(recipients),
        "key": "value",
        "Vars": {
            "other-key": "other-value",
            "env": "-development",
        },
    }

    def test_send(self):
        successful = mails.send(recipients=self.recipients, data=self.data)
        assert successful
        email = Email.query.one()
        assert email.status == EmailStatus.SENT
        assert email.content == self.expected_sent_data

    @override_settings(MAILJET_EMAIL_BACKEND="pcapi.core.mails.backends.testing.FailingBackend")
    def test_send_failure(self):
        successful = mails.send(recipients=self.recipients, data=self.data)
        assert not successful
        email = Email.query.one()
        assert email.status == EmailStatus.ERROR
        assert email.content == self.expected_sent_data

    @override_settings(MAILJET_EMAIL_BACKEND="pcapi.core.mails.backends.mailjet.MailjetBackend")
    def test_send_with_mailjet(self):
        expected = copy.deepcopy(self.expected_sent_data)
        expected["MJ-TemplateErrorReporting"] = "dev@example.com"
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            successful = mails.send(recipients=self.recipients, data=copy.deepcopy(self.data))
            assert posted.last_request.json() == expected
        assert successful


class MailjetBackendTest:

    recipients = ["recipient1@example.com", "recipient2@example.com"]
    data = {"key": "value", "Vars": {"other-key": "other-value"}}
    expected_sent_data = {
        "FromEmail": "support@example.com",
        "To": ", ".join(recipients),
        "key": "value",
        "Vars": {
            "other-key": "other-value",
            "env": "-development",
        },
        "MJ-TemplateErrorReporting": "dev@example.com",
    }

    def _get_backend(self):
        return pcapi.core.mails.backends.mailjet.MailjetBackend()

    def test_send_mail(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert posted.last_request.json() == self.expected_sent_data
        assert result.successful

    def test_send_mail_with_error_response(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send", status_code=400)
            result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert posted.last_request.json() == self.expected_sent_data
        assert not result.successful

    def test_send_mail_with_timeout(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            mock.post("https://api.mailjet.com/v3/send", exc=requests.exceptions.ConnectTimeout)
            result = backend.send_mail(recipients=self.recipients, data=self.data)
        assert not result.successful

    @patch("pcapi.utils.requests.logger.info")
    def test_use_our_requests_wrapper_that_logs(self, mocked_logger):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            backend.send_mail(recipients=self.recipients, data=self.data)

        assert posted.last_request.json() == self.expected_sent_data
        mocked_logger.assert_called_once()


class ToDevMailjetBackendTest:
    recipients = ["real1@example.com", "real2@example.com"]
    data = {"key": "value"}
    expected_sent_data = {
        "FromEmail": "support@example.com",
        "To": ", ".join(recipients),
        "key": "value",
        "MJ-TemplateErrorReporting": "dev@example.com",
    }

    def _get_backend(self):
        return pcapi.core.mails.backends.mailjet.ToDevMailjetBackend()

    def test_send_mail_overrides_recipients(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            result = backend.send_mail(recipients=self.recipients, data=self.data)

        expected = copy.deepcopy(self.expected_sent_data)
        expected["To"] = "dev@example.com"
        assert posted.last_request.json() == expected
        assert result.successful

    @override_settings(WHITELISTED_EMAIL_RECIPIENTS=["false1@example.com", "real2@example.com"])
    def test_send_mail_if_any_recipient_is_whitelisted(self):
        backend = self._get_backend()
        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert posted.last_request.json() == self.expected_sent_data
        assert result.successful

    def test_send_mail_inject_preamble_in_html(self):
        backend = self._get_backend()
        data = copy.deepcopy(self.data)
        data["Html-part"] = "<div>some HTML...<div>"

        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api.mailjet.com/v3/send")
            result = backend.send_mail(recipients=self.recipients, data=data)

        expected = copy.deepcopy(self.expected_sent_data)
        expected["To"] = "dev@example.com"
        posted_json = posted.last_request.json()
        assert posted_json["Html-part"].endswith("<div>some HTML...<div>")
        assert "would have been sent to real1@example.com, real2@example.com" in posted_json["Html-part"]
        assert result.successful


class SendinblueBackendTest:

    recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]
    mock_template = sendinblue_models.Template(
        id_prod=1, id_not_prod=10, tags=["this_is_such_a_great_tag", "it_would_be_a_pity_if_anything_happened_to_it"]
    )
    mock_reply_to = sendinblue_models.EmailInfo(email="reply_to@example.com", name="Tom S.")
    params = {"Name": "Lucy", "City": "Kennet", "OtherCharacteristics": "Awsomeness"}
    data = sendinblue_models.SendinblueTransactionalEmailData(
        template=mock_template, params=params, reply_to=mock_reply_to
    )

    expected_sent_data = sendinblue_tasks.SendTransactionalEmailRequest(
        recipients=recipients,
        params=params,
        template_id=data.template.id,
        tags=data.template.tags,
        sender=dataclasses.asdict(sendinblue_models.SendinblueTransactionalSender.SUPPORT.value),
        reply_to={"email": "reply_to@example.com", "name": "Tom S."},
    )

    def _get_backend(self):
        return pcapi.core.mails.backends.sendinblue.SendinblueBackend()

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail(self, mock_send_transactional_email_secondary_task):
        backend = self._get_backend()
        result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == list(self.expected_sent_data.recipients)
        assert task_param.params == self.expected_sent_data.params
        assert task_param.template_id == self.expected_sent_data.template_id
        assert task_param.tags == self.expected_sent_data.tags
        assert task_param.sender == self.expected_sent_data.sender
        assert task_param.reply_to == self.expected_sent_data.reply_to
        assert result.successful

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_with_no_reply_equal_overrided_by_sender(self, mock_send_transactional_email_secondary_task):

        self.data = sendinblue_models.SendinblueTransactionalEmailData(
            template=self.mock_template, params=self.params, reply_to=None
        )

        expected_sent_data = sendinblue_tasks.SendTransactionalEmailRequest(
            recipients=self.recipients,
            params=SendinblueBackendTest.params,
            template_id=SendinblueBackendTest.data.template.id,
            tags=SendinblueBackendTest.data.template.tags,
            sender=dataclasses.asdict(sendinblue_models.SendinblueTransactionalSender.SUPPORT.value),
            reply_to=dataclasses.asdict(sendinblue_models.SendinblueTransactionalSender.SUPPORT.value),
        )

        backend = self._get_backend()
        result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == list(self.expected_sent_data.recipients)
        assert task_param.params == expected_sent_data.params
        assert task_param.template_id == expected_sent_data.template_id
        assert task_param.tags == expected_sent_data.tags
        assert task_param.sender == expected_sent_data.sender
        assert task_param.reply_to == expected_sent_data.reply_to
        assert result.successful


@pytest.mark.usefixtures("db_session")
class ToDevSendinblueBackendTest(SendinblueBackendTest):

    expected_sent_data = sendinblue_tasks.SendTransactionalEmailRequest(
        recipients=["dev@example.com"],
        params=SendinblueBackendTest.params,
        template_id=SendinblueBackendTest.data.template.id,
        tags=SendinblueBackendTest.data.template.tags,
        sender=dataclasses.asdict(sendinblue_models.SendinblueTransactionalSender.SUPPORT.value),
        reply_to={"email": "reply_to@example.com", "name": "Tom S."},
    )

    def _get_backend(self):
        return pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend()

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_to_dev(self, mock_send_transactional_email_secondary_task):
        backend = self._get_backend()
        result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == list(self.expected_sent_data.recipients)
        assert task_param.params == self.expected_sent_data.params
        assert task_param.template_id == self.expected_sent_data.template_id
        assert task_param.tags == self.expected_sent_data.tags
        assert task_param.sender == self.expected_sent_data.sender
        assert task_param.reply_to == self.expected_sent_data.reply_to
        assert result.successful

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_test_user(self, mock_send_transactional_email_secondary_task):
        users_factories.UserFactory(email=self.recipients[0], roles=[users_models.UserRole.TEST])

        backend = self._get_backend()
        result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == list(self.recipients[0:1])
        assert result.successful

    @override_settings(WHITELISTED_EMAIL_RECIPIENTS=["whitelisted@example.com", "avery.kelly@example.com"])
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_whitelisted(self, mock_send_transactional_email_secondary_task):
        users_factories.UserFactory(email="avery.kelly@example.com", roles=[users_models.UserRole.TEST])

        backend = self._get_backend()
        result = backend.send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == ["avery.kelly@example.com"]
        assert result.successful
