from unittest.mock import patch

import pytest

# from pcapi.core.mails.backends import sendinblue
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import Template
from pcapi.tasks.serialization.sendinblue_tasks import SendTransactionalEmailRequest
from pcapi.utils.module_loading import import_string


class SendinblueBackendTest:

    recipients = ["lucy.ellingson@example.com", "avery.kelly@example.com"]
    mock_template = Template(
        id_prod=1, id_not_prod=10, tags=["this_is_such_a_great_tag", "it_would_be_a_pity_if_anything_happened_to_it"]
    )
    params = {"Name": "Lucy", "City": "Kennet", "OtherCharacteristics": "Awsomeness"}
    data = SendinblueTransactionalEmailData(template=mock_template, params=params)

    expected_sent_data = SendTransactionalEmailRequest(
        recipients=recipients,
        params=params,
        template_id=data.template.id,
        tags=data.template.tags,
    )

    def _get_backend(self, path_str):
        return import_string(path_str)

    @patch("pcapi.core.mails.backends.sendinblue.send_transactional_email_task.delay")
    @pytest.mark.parametrize(
        "backend_import_string",
        (
            "pcapi.core.mails.backends.sendinblue.SendinblueBackend",
            "pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend",
        ),
    )
    def test_send_mail(self, mock_send_transactional_email_task, backend_import_string):
        backend = self._get_backend(backend_import_string)
        result = backend().send_mail(recipients=self.recipients, data=self.data)

        assert list(mock_send_transactional_email_task.call_args[0][0].recipients) == list(
            self.expected_sent_data.recipients
        )
        assert mock_send_transactional_email_task.call_args[0][0].params == self.expected_sent_data.params
        assert mock_send_transactional_email_task.call_args[0][0].template_id == self.expected_sent_data.template_id
        assert mock_send_transactional_email_task.call_args[0][0].tags == self.expected_sent_data.tags
        assert result.successful
