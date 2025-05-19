import logging
from unittest.mock import patch

import pytest
from brevo_python.rest import ApiException as SendinblueApiException
from urllib3.response import HTTPResponse

from pcapi.core.mails import models
from pcapi.core.mails import send
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
        reply_to={"email": "reply_to@example.com", "name": "Tom S."},
        enable_unsubscribe=False,
    )

    def _get_backend_for_test(self):
        return import_string("pcapi.core.mails.backends.sendinblue.SendinblueBackend")

    @pytest.mark.settings(
        WHITELISTED_EMAIL_RECIPIENTS=[
            "lucy.ellingson@example.com",
            "avery.kelly@example.com",
            "catherine.clark@example.com",
            "tate.walker@example.com",
        ]
    )
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail(self, mock_send_transactional_email_secondary_task_cloud_tasks):
        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=False).send_mail(
            recipients=self.recipients, bcc_recipients=self.bcc_recipients, data=self.data
        )

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        task_param = mock_send_transactional_email_secondary_task_cloud_tasks.call_args[0][0]

        assert set(task_param.recipients) == set(self.expected_sent_data.recipients)
        assert set(task_param.bcc_recipients) == set(self.expected_sent_data.bcc_recipients)
        assert task_param.params == self.expected_sent_data.params
        assert task_param.template_id == self.expected_sent_data.template_id
        assert task_param.tags == self.expected_sent_data.tags
        assert task_param.reply_to == self.expected_sent_data.reply_to
        assert task_param.enable_unsubscribe == self.expected_sent_data.enable_unsubscribe

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail_with_no_sender(self, mock_send_transactional_email_secondary_task_cloud_tasks):
        self.mock_template = models.TemplatePro(
            id_prod=1,
            id_not_prod=10,
            tags=["this_is_such_a_great_tag", "it_would_be_a_pity_if_anything_happened_to_it"],
        )
        self.data = models.TransactionalEmailData(template=self.mock_template, params=self.params, reply_to=None)

        expected_sent_data = sendinblue_tasks.SendTransactionalEmailRequest(
            recipients=self.recipients,
            params=self.params,
            template_id=self.data.template.id,
            tags=self.data.template.tags,
            sender=None,
            reply_to=None,
            enable_unsubscribe=False,
        )

        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=True).send_mail(
            recipients=self.recipients, bcc_recipients=self.bcc_recipients, data=self.data
        )

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        task_param = mock_send_transactional_email_secondary_task_cloud_tasks.call_args[0][0]

        assert task_param.params == expected_sent_data.params
        assert task_param.template_id == expected_sent_data.template_id
        assert task_param.tags == expected_sent_data.tags
        assert task_param.sender == expected_sent_data.sender
        assert task_param.reply_to == expected_sent_data.reply_to
        assert task_param.enable_unsubscribe == self.expected_sent_data.enable_unsubscribe

    @patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.delete_contact")
    @patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.create_contact")
    def test_create_contact(self, mock_create_contact, mock_delete_contact):
        payload = sendinblue_tasks.UpdateSendinblueContactRequest(
            email="old.email@example.com",
            use_pro_subaccount=True,
            attributes={"EMAIL": "new.email@example.com"},
            contact_list_ids=[123],
            emailBlacklisted=False,
        )

        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=True).create_contact(payload)

        mock_create_contact.assert_called_once()
        mock_delete_contact.assert_not_called()

    @patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.delete_contact")
    @patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.create_contact")
    def test_create_contact_duplicate_email(self, mock_create_contact, mock_delete_contact):
        payload = sendinblue_tasks.UpdateSendinblueContactRequest(
            email="old.email@example.com",
            use_pro_subaccount=True,
            attributes={"EMAIL": "new.email@example.com"},
            contact_list_ids=[123],
            emailBlacklisted=False,
        )

        mock_create_contact.side_effect = SendinblueApiException(
            http_resp=HTTPResponse(
                status=400,
                reason="Bad Request",
                headers={"Content-Type": "application/json"},
                body='{"code":"duplicate_parameter",'
                '"message":"Unable to update contact, email is already associated with another Contact",'
                '"metadata":{"duplicate_identifiers":["email"]}}',
            )
        )

        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=True).create_contact(payload)

        mock_create_contact.assert_called_once()
        mock_delete_contact.assert_called_once_with("old.email@example.com")


@pytest.mark.usefixtures("db_session")
class ToDevSendinblueBackendTest(SendinblueBackendTest):
    expected_sent_data_to_dev = sendinblue_tasks.SendTransactionalEmailRequest(
        recipients=["dev@example.com"],
        bcc_recipients=["test@example.com"],
        params=SendinblueBackendTest.params,
        template_id=SendinblueBackendTest.data.template.id,
        tags=SendinblueBackendTest.data.template.tags,
        sender=None,
        reply_to={"email": "reply_to@example.com", "name": "Tom S."},
        enable_unsubscribe=SendinblueBackendTest.data.template.enable_unsubscribe,
    )

    def _get_backend_for_test(self):
        return import_string("pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")

    @pytest.mark.settings(WHITELISTED_EMAIL_RECIPIENTS=["test@example.com"])
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail_to_dev(self, mock_send_transactional_email_secondary_task_cloud_tasks):
        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=False).send_mail(
            recipients=self.recipients, bcc_recipients=["test@example.com"], data=self.data
        )

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        task_param = mock_send_transactional_email_secondary_task_cloud_tasks.call_args[0][0]
        assert set(task_param.recipients) == set(self.expected_sent_data_to_dev.recipients)
        assert set(task_param.bcc_recipients) == set(self.expected_sent_data_to_dev.bcc_recipients)
        assert task_param.params == self.expected_sent_data_to_dev.params
        assert task_param.template_id == self.expected_sent_data_to_dev.template_id
        assert task_param.tags == self.expected_sent_data_to_dev.tags
        assert task_param.sender == self.expected_sent_data_to_dev.sender
        assert task_param.reply_to == self.expected_sent_data_to_dev.reply_to

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail_test_user(self, mock_send_transactional_email_secondary_task_cloud_tasks):
        users_factories.UserFactory(email=self.recipients[0], roles=[users_models.UserRole.TEST])

        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=False).send_mail(recipients=self.recipients, data=self.data)

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        task_param = mock_send_transactional_email_secondary_task_cloud_tasks.call_args[0][0]
        assert list(task_param.recipients) == list(self.recipients[0:1])

    @pytest.mark.parametrize(
        "recipient",
        ["avery.kelly@example.com", "sandy.zuko@passculture-test.app"],
    )
    @pytest.mark.settings(WHITELISTED_EMAIL_RECIPIENTS=["avery.kelly@example.com", "*@passculture-test.app"])
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail_whitelisted(self, mock_send_transactional_email_secondary_task_cloud_tasks, recipient):
        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=False).send_mail(
            recipients=[recipient, "lucy.ellingson@example.com"], data=self.data
        )

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        task_param = mock_send_transactional_email_secondary_task_cloud_tasks.call_args[0][0]
        assert list(task_param.recipients) == [recipient]

    @pytest.mark.settings(IS_STAGING=True, IS_E2E_TESTS=True, END_TO_END_TESTS_EMAIL_ADDRESS="qa-test@passculture.app")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail_whitelisted_qa_staging(self, mock_send_transactional_email_secondary_task_cloud_tasks):
        recipient = "qa-test+123@passculture.app"
        users_factories.UserFactory(email=recipient)

        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=False).send_mail(recipients=[recipient], data=self.data)

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        task_param = mock_send_transactional_email_secondary_task_cloud_tasks.call_args[0][0]
        assert list(task_param.recipients) == [recipient]

    @pytest.mark.settings(IS_TESTING=True, IS_E2E_TESTS=True, END_TO_END_TESTS_EMAIL_ADDRESS="qa-test@passculture.app")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail_whitelisted_qa_testing(
        self, mock_send_transactional_email_secondary_task_cloud_tasks, recipient="qa-test+123@passculture.app"
    ):
        users_factories.UserFactory(email=recipient)

        backend = self._get_backend_for_test()
        backend(use_pro_subaccount=False).send_mail(recipients=[recipient], data=self.data)

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        task_param = mock_send_transactional_email_secondary_task_cloud_tasks.call_args[0][0]
        assert list(task_param.recipients) == [recipient]


class SendTest:
    @pytest.mark.settings(IS_TESTING=True, EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_to_ehp_false_in_testing(self, mock_send_transactional_email_secondary_task_cloud_tasks, caplog):
        mock_template_send_ehp_false = models.Template(
            id_prod=11, id_not_prod=12, tags=["some", "stuff"], send_to_ehp=False
        )
        mock_reply_to = models.EmailInfo(email="reply_to@example.com", name="Tom S.")
        data = models.TransactionalEmailData(template=mock_template_send_ehp_false, params={}, reply_to=mock_reply_to)
        recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]

        with caplog.at_level(logging.INFO):
            send(recipients=recipients, data=data)

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 0

        assert caplog.messages[0] == (
            "An email would be sent via Sendinblue to=lucy.ellingson@example.com, avery.kelly@example.com, bcc=(): "
            "{'template': {'id_prod': 11, 'id_not_prod': 12, 'tags': ['some', 'stuff'], 'use_priority_queue': False, "
            "'send_to_ehp': False, 'enable_unsubscribe': False}, "
            "'reply_to': {'email': 'reply_to@example.com', 'name': 'Tom S.'}, 'params': {}}"
        )

    @pytest.mark.settings(IS_TESTING=True, EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_to_ehp_true_in_testing(self, mock_send_transactional_email_secondary_task_cloud_tasks, caplog):
        mock_template_send_ehp_true = models.Template(
            id_prod=11, id_not_prod=12, tags=["some", "stuff"], send_to_ehp=True
        )
        mock_reply_to = models.EmailInfo(email="reply_to@example.com", name="Tom S.")
        data = models.TransactionalEmailData(template=mock_template_send_ehp_true, params={}, reply_to=mock_reply_to)
        recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]

        with caplog.at_level(logging.INFO):
            send(recipients=recipients, data=data)

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        assert caplog.records == []

    @pytest.mark.parametrize(
        "template_class,expected_use_pro_subaccount",
        [
            (models.TemplatePro, True),
            (models.Template, False),
        ],
    )
    @pytest.mark.settings(EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.SendinblueBackend")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail_to_pro(
        self,
        mock_send_transactional_email_secondary_task_cloud_tasks,
        caplog,
        template_class,
        expected_use_pro_subaccount,
    ):
        mock_template = template_class(id_prod=1, id_not_prod=10, send_to_ehp=False)
        data = models.TransactionalEmailData(template=mock_template)
        recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]

        with caplog.at_level(logging.INFO):
            send(recipients=recipients, data=data)

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 1
        assert (
            mock_send_transactional_email_secondary_task_cloud_tasks.call_args[0][0].use_pro_subaccount
            is expected_use_pro_subaccount
        )

    @pytest.mark.parametrize(
        "template_class,enable_unsubscribe,expected_use_pro_subaccount",
        [
            (models.TemplatePro, True, True),
            (models.Template, False, False),
        ],
    )
    @pytest.mark.settings(IS_TESTING=True, EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.SendinblueBackend")
    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_secondary_task_cloud_tasks.delay")
    def test_send_mail_to_pro_in_ehp(
        self,
        mock_send_transactional_email_secondary_task_cloud_tasks,
        features,
        caplog,
        template_class,
        enable_unsubscribe,
        expected_use_pro_subaccount,
    ):
        mock_template = template_class(
            id_prod=1, id_not_prod=10, send_to_ehp=False, enable_unsubscribe=enable_unsubscribe
        )
        data = models.TransactionalEmailData(template=mock_template)
        recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]

        with caplog.at_level(logging.INFO):
            send(recipients=recipients, data=data)

        assert mock_send_transactional_email_secondary_task_cloud_tasks.call_count == 0
        assert caplog.messages[0] == (
            f"An email would be sent via Sendinblue {'using the PRO subaccount ' if expected_use_pro_subaccount else ''}to=lucy.ellingson@example.com, "
            "avery.kelly@example.com, bcc=(): {'template': {'id_prod': 1, 'id_not_prod': 10, 'tags': [], 'use_priority_queue': False, "
            f"'send_to_ehp': False, 'enable_unsubscribe': {enable_unsubscribe}"
            "}, 'reply_to': None, 'params': {}}"
        )
