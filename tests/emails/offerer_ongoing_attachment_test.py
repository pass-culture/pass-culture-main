from unittest.mock import patch

import pytest

from pcapi.emails.offerer_ongoing_attachment import retrieve_data_for_offerer_ongoing_attachment_email
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository


class ProOffererAttachmentValidationEmailTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.emails.offerer_ongoing_attachment.feature_send_mail_to_users_enabled", return_value=False)
    @patch("pcapi.emails.offerer_ongoing_attachment.format_environment_for_email", return_value="-testing")
    @patch("pcapi.emails.offerer_ongoing_attachment.find_user_offerer_email", return_value="pro@example.com")
    def test_should_return_data_email_with_dev_email_address_when_not_in_production(
        self, feature_send_mail_to_users_enabled, format_environment_for_email, find_user_offerer_email, app
    ):
        # Given
        offerer = create_offerer(name="Le Théâtre SAS")
        pro_user = create_user()
        user_offerer = create_user_offerer(pro_user, offerer)

        repository.save(pro_user, user_offerer)

        # When
        offerer_attachment_validation_email = retrieve_data_for_offerer_ongoing_attachment_email(user_offerer)

        # Then
        assert offerer_attachment_validation_email == {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 778749,
            "MJ-TemplateLanguage": True,
            "To": "dev@example.com",
            "Vars": {"nom_structure": "Le Théâtre SAS", "env": "-testing"},
        }

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.emails.offerer_ongoing_attachment.feature_send_mail_to_users_enabled", return_value=True)
    @patch("pcapi.emails.offerer_ongoing_attachment.format_environment_for_email", return_value="")
    @patch("pcapi.emails.offerer_ongoing_attachment.find_user_offerer_email", return_value="pro@example.com")
    def test_should_return_data_email_with_pro_email_address_when_environment_is_production(
        self, feature_send_mail_to_users_enabled, format_environment_for_email, find_user_offerer_email, app
    ):
        # Given
        offerer = create_offerer(name="Le Théâtre SAS")
        pro_user = create_user(email="pro@example.com")
        user_offerer = create_user_offerer(pro_user, offerer)

        repository.save(user_offerer)

        # When
        offerer_attachment_validation_email = retrieve_data_for_offerer_ongoing_attachment_email(user_offerer)

        # Then
        assert offerer_attachment_validation_email == {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 778749,
            "MJ-TemplateLanguage": True,
            "To": "pro@example.com",
            "Vars": {"nom_structure": "Le Théâtre SAS", "env": ""},
        }
