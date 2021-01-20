from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time

from pcapi import settings
from pcapi.core.users import factories as users_factories
from pcapi.emails import beneficiary_activation
from pcapi.model_creators.generic_creators import create_user


class GetActivationEmailTest:
    @patch("pcapi.settings.IS_PROD", return_value=True)
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
        assert activation_email_data["To"] == settings.DEV_EMAIL_ADDRESS
        assert activation_email_data["Vars"] == {
            "prenom_user": "Fabien",
            "token": "ABCD123",
            "email": "fabien%2Btest%40example.net",
            "env": "-development",
        }

    @freeze_time("2013-05-15 09:00:00")
    def test_return_dict_for_native_eligible_user(self):
        # Given
        user = create_user(email="fabien+test@example.net", date_of_birth=datetime(1995, 2, 5))
        token = users_factories.EmailValidationToken.build(user=user)

        # When
        activation_email_data = beneficiary_activation.get_activation_email_data_for_native(user, token)

        # Then
        assert activation_email_data["Vars"]["nativeAppLink"]
        assert "email=fabien%2Btest%40example.net" in activation_email_data["Vars"]["nativeAppLink"]
        assert activation_email_data["Vars"]["isEligible"] is True
        assert activation_email_data["Vars"]["isMinor"] is False

    @freeze_time("2011-05-15 09:00:00")
    def test_return_dict_for_native_under_age_user(self):
        # Given
        user = create_user(email="fabien+test@example.net", date_of_birth=datetime(1995, 2, 5))
        token = users_factories.EmailValidationToken.build(user=user)

        # When
        activation_email_data = beneficiary_activation.get_activation_email_data_for_native(user, token)

        # Then
        assert activation_email_data["Vars"]["nativeAppLink"]
        assert "email=fabien%2Btest%40example.net" in activation_email_data["Vars"]["nativeAppLink"]
        assert activation_email_data["Vars"]["isEligible"] is False
        assert activation_email_data["Vars"]["isMinor"] is True
