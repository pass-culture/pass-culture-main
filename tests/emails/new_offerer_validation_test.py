from unittest.mock import patch

from pcapi.emails.new_offerer_validation import retrieve_data_for_new_offerer_validation_email
from pcapi.model_creators.generic_creators import create_offerer


class MakeNewOffererValidationEmailTest:
    @patch("pcapi.emails.new_offerer_validation.feature_send_mail_to_users_enabled", return_value=False)
    @patch("pcapi.emails.new_offerer_validation.format_environment_for_email", return_value="-testing")
    @patch("pcapi.emails.new_offerer_validation.find_new_offerer_user_email", return_value="admin@example.com")
    def test_email_is_sent_to_dev_at_passculture_when_not_production_environment(
        self, feature_send_mail_to_users_enabled, format_environment_for_email, find_new_offerer_user_email
    ):
        # Given
        offerer = create_offerer(name="Le Théâtre SAS")

        # When
        new_offerer_validation_email = retrieve_data_for_new_offerer_validation_email(offerer)

        # Then
        assert new_offerer_validation_email == {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 778723,
            "MJ-TemplateLanguage": True,
            "To": "dev@example.com",
            "Vars": {"offerer_name": "Le Théâtre SAS", "env": "-testing"},
        }

    @patch("pcapi.emails.new_offerer_validation.feature_send_mail_to_users_enabled", return_value=True)
    @patch("pcapi.emails.new_offerer_validation.format_environment_for_email", return_value="")
    @patch("pcapi.emails.new_offerer_validation.find_new_offerer_user_email", return_value="admin@example.com")
    def test_email_is_sent_to_user_offerer_when_environment_is_production(
        self, feature_send_mail_to_users_enabled, format_environment_for_email, find_new_offerer_user_email
    ):
        # Given
        offerer = create_offerer(name="Le Théâtre SAS")

        # When
        new_offerer_validation_email = retrieve_data_for_new_offerer_validation_email(offerer)

        # Then
        assert new_offerer_validation_email == {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 778723,
            "MJ-TemplateLanguage": True,
            "To": "admin@example.com",
            "Vars": {"offerer_name": "Le Théâtre SAS", "env": ""},
        }
