from unittest.mock import patch

from pcapi.emails.pro_waiting_validation import retrieve_data_for_pro_user_waiting_offerer_validation_email
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user


class MakeProUserWaitingForValidationByAdminEmailTest:
    def test_should_return_mailjet_data_with_dev_email_when_not_in_production(self):
        # Given
        user = create_user()
        user.generate_validation_token()
        offerer = create_offerer(name="Bar des amis")

        # When
        mailjet_data = retrieve_data_for_pro_user_waiting_offerer_validation_email(user, offerer)

        # Then
        assert mailjet_data == {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 778329,
            "MJ-TemplateLanguage": True,
            "To": "dev@example.com",
            "Vars": {"nom_structure": "Bar des amis"},
        }

    @patch("pcapi.emails.pro_waiting_validation.feature_send_mail_to_users_enabled", return_value=True)
    def test_should_return_mailjet_data_with_user_email_when_in_production(
        self, mock_feature_send_mail_to_users_enabled
    ):
        # Given
        user = create_user(email="user@example.com")
        user.generate_validation_token()
        offerer = create_offerer(name="Bar des amis")

        # When
        mailjet_data = retrieve_data_for_pro_user_waiting_offerer_validation_email(user, offerer)

        # Then
        assert mailjet_data == {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 778329,
            "MJ-TemplateLanguage": True,
            "To": "user@example.com",
            "Vars": {"nom_structure": "Bar des amis"},
        }
