from unittest.mock import patch

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.domain.pro_emails import send_attachment_validation_email_to_pro_offerer


class SendAttachmentValidationEmailToProOffererTest:
    @patch("pcapi.domain.pro_emails.retrieve_data_for_offerer_attachment_validation_email")
    @pytest.mark.usefixtures("db_session")
    def test_send_attachment_validation_email_to_pro_offerer(
        self, mocked_retrieve_data_for_offerer_attachment_validation_email, app
    ):
        # given
        user_offerer = UserOffererFactory()
        mocked_retrieve_data_for_offerer_attachment_validation_email.return_value = {"Html-part": ""}

        # when
        send_attachment_validation_email_to_pro_offerer(user_offerer)

        # then
        mocked_retrieve_data_for_offerer_attachment_validation_email.assert_called_once_with(user_offerer.offerer)
        assert mails_testing.outbox[0].sent_data["Html-part"] == ""
