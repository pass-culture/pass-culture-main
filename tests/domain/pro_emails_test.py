from unittest.mock import patch

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.domain.pro_emails import send_attachment_validation_email_to_pro_offerer
from pcapi.domain.pro_emails import send_validation_confirmation_email_to_pro


@pytest.mark.usefixtures("db_session")
class SendValidationConfirmationEmailTest:
    @patch(
        "pcapi.domain.pro_emails.retrieve_data_for_new_offerer_validation_email",
        return_value={"Mj-TemplateID": 778723},
    )
    def when_feature_send_mail_to_users_is_enabled_sends_email_to_all_users_linked_to_offerer(
        self, mock_retrieve_data_for_new_offerer_validation_email
    ):
        # Given
        offerer = UserOffererFactory().offerer

        # When
        send_validation_confirmation_email_to_pro(offerer)

        # Then
        mock_retrieve_data_for_new_offerer_validation_email.assert_called_once_with(offerer)
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 778723


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
