from unittest.mock import patch

from pcapi.core.users import factories as users_factories
from pcapi.emails import beneficiary_activation
from pcapi.model_creators.generic_creators import create_user


class GetActivationEmailTest:
    @patch("pcapi.emails.beneficiary_activation.format_environment_for_email", return_value="")
    def test_should_return_dict_when_environment_is_production(self, mock_format_environment_for_email):
        # Given
        user = create_user(email="fabien+test@example.net", first_name="Fabien", reset_password_token="ABCD123")

        # When
        activation_email_data = beneficiary_activation.get_activation_email_data(user)

        # Then
        assert activation_email_data == {
            "FromEmail": "support@example.com",
            "Mj-TemplateID": 994771,
            "Mj-TemplateLanguage": True,
            "To": "fabien+test@example.net",
            "Vars": {"prenom_user": "Fabien", "token": "ABCD123", "email": "fabien%2Btest%40example.net", "env": ""},
        }

    @patch("pcapi.emails.beneficiary_activation.format_environment_for_email", return_value="-development")
    def test_should_return_dict_when_environment_is_development(self, mock_format_environment_for_email):
        # Given
        user = create_user(email="fabien+test@example.net", first_name="Fabien", reset_password_token="ABCD123")

        # When
        activation_email_data = beneficiary_activation.get_activation_email_data(user)

        # Then
        assert activation_email_data["Vars"] == {
            "prenom_user": "Fabien",
            "token": "ABCD123",
            "email": "fabien%2Btest%40example.net",
            "env": "-development",
        }

    def test_return_dict_for_native(self):
        # Given
        user = create_user(email="fabien+test@example.net")
        token = users_factories.EmailValidationToken.build(user=user)

        # When
        activation_email_data = beneficiary_activation.get_activation_email_data_for_native(user, token)

        # Then
        assert activation_email_data["Vars"]["native_app_link"]
