import dataclasses
import logging
from unittest.mock import patch

import pytest

from pcapi.core.mails import models
from pcapi.core.mails import send
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.tasks.serialization import sendinblue_tasks
from pcapi.utils.module_loading import import_string


@pytest.mark.usefixtures("db_session")
class SendinblueBackendTest:
    recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]
    bcc_recipients = ["catherine.clark@example.com", "tate.walker@example.com"]
    mock_template = models.Template(
        id_prod=1, id_not_prod=10, tags=["this_is_such_a_great_tag", "it_would_be_a_pity_if_anything_happened_to_it"]
    )
    mock_reply_to = models.EmailInfo(email="reply_to@example.com", name="Tom S.")
    params = {"Name": "Lucy", "City": "Kennet", "OtherCharacteristics": "Awsomeness"}
    data = models.TransactionalEmailData(template=mock_template, params=params, reply_to=mock_reply_to)

    expected_sent_data = sendinblue_tasks.SendTransactionalEmailRequest(
        recipients=recipients,
        bcc_recipients=bcc_recipients,
        params=params,
        template_id=data.template.id,
        tags=data.template.tags,
        sender=dataclasses.asdict(models.TransactionalSender.SUPPORT.value),
        reply_to={"email": "reply_to@example.com", "name": "Tom S."},
    )

    def _get_backend_for_test(self):
        return import_string("pcapi.core.mails.backends.sendinblue.SendinblueBackend")

    @override_settings(
        WHITELISTED_EMAIL_RECIPIENTS=[
            "lucy.ellingson@example.com",
            "avery.kelly@example.com",
            "catherine.clark@example.com",
            "tate.walker@example.com",
        ]
    )
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail(self, mock_send_transactional_email_secondary_task):
        backend = self._get_backend_for_test()
        backend().send_mail(recipients=self.recipients, bcc_recipients=self.bcc_recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]

        assert set(task_param.recipients) == set(self.expected_sent_data.recipients)
        assert set(task_param.bcc_recipients) == set(self.expected_sent_data.bcc_recipients)
        assert task_param.params == self.expected_sent_data.params
        assert task_param.template_id == self.expected_sent_data.template_id
        assert task_param.tags == self.expected_sent_data.tags
        assert task_param.sender == self.expected_sent_data.sender
        assert task_param.reply_to == self.expected_sent_data.reply_to

    @override_settings(WHITELISTED_EMAIL_RECIPIENTS=["lucy.ellingson@example.com", "avery.kelly@example.com"])
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_with_no_reply_equal_overrided_by_sender(self, mock_send_transactional_email_secondary_task):
        self.data = models.TransactionalEmailData(template=self.mock_template, params=self.params, reply_to=None)

        expected_sent_data_no_reply = sendinblue_tasks.SendTransactionalEmailRequest(
            recipients=self.recipients,
            params=SendinblueBackendTest.params,
            template_id=SendinblueBackendTest.data.template.id,
            tags=SendinblueBackendTest.data.template.tags,
            sender=dataclasses.asdict(models.TransactionalSender.SUPPORT.value),
            reply_to=dataclasses.asdict(models.TransactionalSender.SUPPORT.value),
        )

        backend = self._get_backend_for_test()
        backend().send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert set(task_param.recipients) == set(expected_sent_data_no_reply.recipients)
        assert task_param.params == expected_sent_data_no_reply.params
        assert task_param.template_id == expected_sent_data_no_reply.template_id
        assert task_param.tags == expected_sent_data_no_reply.tags
        assert task_param.sender == expected_sent_data_no_reply.sender
        assert task_param.reply_to == expected_sent_data_no_reply.reply_to


@pytest.mark.usefixtures("db_session")
class ToDevSendinblueBackendTest(SendinblueBackendTest):
    expected_sent_data_to_dev = sendinblue_tasks.SendTransactionalEmailRequest(
        recipients=["dev@example.com"],
        bcc_recipients=["test@example.com"],
        params=SendinblueBackendTest.params,
        template_id=SendinblueBackendTest.data.template.id,
        tags=SendinblueBackendTest.data.template.tags,
        sender=dataclasses.asdict(models.TransactionalSender.SUPPORT.value),
        reply_to={"email": "reply_to@example.com", "name": "Tom S."},
    )

    def _get_backend_for_test(self):
        return import_string("pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")

    @override_settings(WHITELISTED_EMAIL_RECIPIENTS=["test@example.com"])
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_to_dev(self, mock_send_transactional_email_secondary_task):
        backend = self._get_backend_for_test()
        backend().send_mail(recipients=self.recipients, bcc_recipients=["test@example.com"], data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert set(task_param.recipients) == set(self.expected_sent_data_to_dev.recipients)
        assert set(task_param.bcc_recipients) == set(self.expected_sent_data_to_dev.bcc_recipients)
        assert task_param.params == self.expected_sent_data_to_dev.params
        assert task_param.template_id == self.expected_sent_data_to_dev.template_id
        assert task_param.tags == self.expected_sent_data_to_dev.tags
        assert task_param.sender == self.expected_sent_data_to_dev.sender
        assert task_param.reply_to == self.expected_sent_data_to_dev.reply_to

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_test_user(self, mock_send_transactional_email_secondary_task):
        users_factories.UserFactory(email=self.recipients[0], roles=[users_models.UserRole.TEST])

        backend = self._get_backend_for_test()
        backend().send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == list(self.recipients[0:1])

    @pytest.mark.parametrize(
        "recipient",
        ["avery.kelly@example.com", "sandy.zuko@passculture-test.app"],
    )
    @override_settings(WHITELISTED_EMAIL_RECIPIENTS=["avery.kelly@example.com", "*@passculture-test.app"])
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_whitelisted(self, mock_send_transactional_email_secondary_task, recipient):
        backend = self._get_backend_for_test()
        backend().send_mail(recipients=[recipient, "lucy.ellingson@example.com"], data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == [recipient]

    @override_settings(IS_STAGING=True, IS_E2E_TESTS=True, END_TO_END_TESTS_EMAIL_ADDRESS="qa-test@passculture.app")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_whitelisted_qa_staging(self, mock_send_transactional_email_secondary_task):
        recipient = "qa-test+123@passculture.app"
        users_factories.UserFactory(email=recipient)

        backend = self._get_backend_for_test()
        backend().send_mail(recipients=[recipient], data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == [recipient]

    @override_settings(IS_TESTING=True, IS_E2E_TESTS=True, END_TO_END_TESTS_EMAIL_ADDRESS="qa-test@passculture.app")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_mail_whitelisted_qa_testing(
        self, mock_send_transactional_email_secondary_task, recipient="qa-test+123@passculture.app"
    ):
        users_factories.UserFactory(email=recipient)

        backend = self._get_backend_for_test()
        backend().send_mail(recipients=[recipient], data=self.data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        task_param = mock_send_transactional_email_secondary_task.call_args[0][0]
        assert list(task_param.recipients) == [recipient]


class SendTest:
    @override_settings(IS_TESTING=True)
    @override_settings(EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_to_ehp_false_in_testing(self, mock_send_transactional_email_secondary_task, caplog):
        mock_template_send_ehp_false = models.Template(
            id_prod=11, id_not_prod=12, tags=["some", "stuff"], send_to_ehp=False
        )
        mock_reply_to = models.EmailInfo(email="reply_to@example.com", name="Tom S.")
        data = models.TransactionalEmailData(template=mock_template_send_ehp_false, params={}, reply_to=mock_reply_to)
        recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]

        with caplog.at_level(logging.INFO):
            send(recipients=recipients, data=data)

        assert mock_send_transactional_email_secondary_task.call_count == 0

        assert caplog.messages[0] == (
            "An email would be sent via Sendinblue to=lucy.ellingson@example.com, avery.kelly@example.com, bcc=(): "
            "{'template': {'id_prod': 11, 'id_not_prod': 12, 'tags': ['some', 'stuff'], 'use_priority_queue': False, "
            "'sender': <TransactionalSender.SUPPORT: EmailInfo(email='support@example.com', name='pass Culture')>, 'send_to_ehp': False}, "
            "'reply_to': {'email': 'reply_to@example.com', 'name': 'Tom S.'}, 'params': {}}"
        )

    @override_settings(IS_TESTING=True)
    @override_settings(EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task.delay")
    def test_send_to_ehp_true_in_testing(self, mock_send_transactional_email_secondary_task, caplog):
        mock_template_send_ehp_true = models.Template(
            id_prod=11, id_not_prod=12, tags=["some", "stuff"], send_to_ehp=True
        )
        mock_reply_to = models.EmailInfo(email="reply_to@example.com", name="Tom S.")
        data = models.TransactionalEmailData(template=mock_template_send_ehp_true, params={}, reply_to=mock_reply_to)
        recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]

        with caplog.at_level(logging.INFO):
            send(recipients=recipients, data=data)

        assert mock_send_transactional_email_secondary_task.call_count == 1
        assert caplog.records == []
