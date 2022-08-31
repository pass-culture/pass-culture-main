import dataclasses
from unittest.mock import patch

import pytest

from pcapi.core.mails import models
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.tasks.serialization import sendinblue_tasks
from pcapi.utils.module_loading import import_string


@pytest.mark.usefixtures("db_session")
class SendinblueBackendTest:
    recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]
    mock_template = models.Template(
        id_prod=1, id_not_prod=10, tags=["this_is_such_a_great_tag", "it_would_be_a_pity_if_anything_happened_to_it"]
    )
    mock_reply_to = models.EmailInfo(email="reply_to@example.com", name="Tom S.")
    params = {"Name": "Lucy", "City": "Kennet", "OtherCharacteristics": "Awsomeness"}
    data = models.SendinblueTransactionalEmailData(template=mock_template, params=params, reply_to=mock_reply_to)

    expected_sent_data = sendinblue_tasks.SendTransactionalEmailRequest(
        recipients=recipients,
        params=params,
        template_id=data.template.id,
        tags=data.template.tags,
        sender=dataclasses.asdict(models.SendinblueTransactionalSender.SUPPORT.value),
        reply_to={"email": "reply_to@example.com", "name": "Tom S."},
    )

    def _get_backend(self):
        return import_string("pcapi.core.mails.backends.sendinblue.SendinblueBackend")

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail(self, mock_send_transactional_email_secondary_task):
        backend = self._get_backend()
        result = backend().send_mail(recipients=self.recipients, data=self.data)

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

        self.data = models.SendinblueTransactionalEmailData(
            template=self.mock_template, params=self.params, reply_to=None
        )

        expected_sent_data = sendinblue_tasks.SendTransactionalEmailRequest(
            recipients=self.recipients,
            params=SendinblueBackendTest.params,
            template_id=SendinblueBackendTest.data.template.id,
            tags=SendinblueBackendTest.data.template.tags,
            sender=dataclasses.asdict(models.SendinblueTransactionalSender.SUPPORT.value),
            reply_to=dataclasses.asdict(models.SendinblueTransactionalSender.SUPPORT.value),
        )

        backend = self._get_backend()
        result = backend().send_mail(recipients=self.recipients, data=self.data)

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
        sender=dataclasses.asdict(models.SendinblueTransactionalSender.SUPPORT.value),
        reply_to={"email": "reply_to@example.com", "name": "Tom S."},
    )

    def _get_backend(self):
        return import_string("pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_to_dev(self, mock_send_transactional_email_secondary_task):
        backend = self._get_backend()
        result = backend().send_mail(recipients=self.recipients, data=self.data)

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
        result = backend().send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == list(self.recipients[0:1])
        assert result.successful

    @override_settings(WHITELISTED_EMAIL_RECIPIENTS=["whitelisted@example.com", "avery.kelly@example.com"])
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_whitelisted(self, mock_send_transactional_email_secondary_task):
        users_factories.UserFactory(email="avery.kelly@example.com", roles=[users_models.UserRole.TEST])

        backend = self._get_backend()
        result = backend().send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == ["avery.kelly@example.com"]
        assert result.successful
