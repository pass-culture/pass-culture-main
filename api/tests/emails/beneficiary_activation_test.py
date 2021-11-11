import pytest

from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.accepted_as_beneficiary_email import (
    get_accepted_as_underage_beneficiary_email_data,
)
from pcapi.core.mails.transactional.users.accepted_as_beneficiary_email import get_accepted_as_beneficiary_email_data
from pcapi.core.mails.transactional.users.email_confirmation_email import get_email_confirmation_email_data
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.emails import beneficiary_activation


pytestmark = pytest.mark.usefixtures("db_session")


class GetActivationEmailTest:
    def test_should_return_dict_when_environment_is_production(self):
        # Given
        user = users_factories.UserFactory.create(email="fabien+test@example.net", firstName="Fabien")
        users_factories.ResetPasswordToken(user=user, value="ABCD123")

        # When
        activation_email_data = beneficiary_activation.get_activation_email_data(user, user.tokens[0])

        # Then
        assert activation_email_data == {
            "Mj-TemplateID": 994771,
            "Mj-TemplateLanguage": True,
            "Vars": {
                "prenom_user": "Fabien",
                "token": "ABCD123",
                "email": "fabien%2Btest%40example.net",
            },
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_should_return_sendinblue_data_when_feature_toggled(self):
        # Given
        user = users_factories.UserFactory.create(email="fabien+test@example.net", firstName="Fabien")
        users_factories.ResetPasswordToken(user=user, value="ABCD123")

        # When
        activation_email_data = get_email_confirmation_email_data(user, user.tokens[0])

        # Then
        assert activation_email_data.template == TransactionalEmail.EMAIL_CONFIRMATION.value
        assert activation_email_data.params["CONFIRMATION_LINK"]
        assert "email%3Dfabien%252Btest%2540example.net" in activation_email_data.params["CONFIRMATION_LINK"]

    def test_return_dict_for_native_eligible_user(self):
        # Given
        user = users_factories.BeneficiaryGrant18Factory.create(email="fabien+test@example.net")
        token = users_factories.EmailValidationToken.build(user=user)

        # When
        activation_email_data = get_email_confirmation_email_data(user, token)

        # Then
        assert activation_email_data["Vars"]["nativeAppLink"]
        assert "email%3Dfabien%252Btest%2540example.net" in activation_email_data["Vars"]["nativeAppLink"]
        assert activation_email_data["Vars"]["isEligible"]
        assert not activation_email_data["Vars"]["isMinor"]
        assert isinstance(activation_email_data["Vars"]["isEligible"], int)
        assert isinstance(activation_email_data["Vars"]["isMinor"], int)

    def test_return_dict_for_native_under_age_user_v2(self):
        # Given
        user = users_factories.UnderageBeneficiaryFactory.create(email="fabien+test@example.net")
        token = users_factories.EmailValidationToken.build(user=user)

        # When
        activation_email_data = get_email_confirmation_email_data(user, token)

        # Then
        assert activation_email_data["Vars"]["nativeAppLink"]
        assert "email%3Dfabien%252Btest%2540example.net" in activation_email_data["Vars"]["nativeAppLink"]
        assert activation_email_data["Vars"]["isEligible"]
        assert activation_email_data["Vars"]["isMinor"]
        assert activation_email_data["Vars"]["depositAmount"] == 300


class GetAcceptedAsBeneficiaryEmailMailjetTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_return_correct_email_metadata(self):
        # Given
        user = users_factories.BeneficiaryGrant18Factory.create(email="fabien+test@example.net")

        # When
        email_data = get_accepted_as_beneficiary_email_data(user)

        assert email_data == {
            "Mj-TemplateID": 2016025,
            "Mj-TemplateLanguage": True,
            "Mj-campaign": "confirmation-credit",
            "Vars": {
                "depositAmount": 300,
            },
        }


class GetAcceptedAsBeneficiaryEmailSendinblueTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_email_metadata(self):
        # Given
        user = users_factories.BeneficiaryGrant18Factory.create(email="fabien+test@example.net")

        # When
        email = get_accepted_as_beneficiary_email_data(user)

        # Then
        assert email.template == TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value
        assert email.params == {"CREDIT": 300}


class GetAcceptedAsUnderageBeneficiaryEmailSendinblueTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_data_for_native_age_17_user_v2(self):
        # Given
        user = users_factories.UnderageBeneficiaryFactory(firstName="Fabien", subscription_age=17)

        # When
        data = get_accepted_as_underage_beneficiary_email_data(user)

        # Then
        assert data.params["FIRSTNAME"] == "Fabien"
        assert data.params["CREDIT"] == 30

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_data_for_native_age_16_user_v2(self):
        # Given

        user = users_factories.UnderageBeneficiaryFactory.create(firstName="Fabien", subscription_age=16)

        # When
        data = get_accepted_as_underage_beneficiary_email_data(user)

        # Then
        assert data.params["FIRSTNAME"] == "Fabien"
        assert data.params["CREDIT"] == 30

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_data_for_native_age_15_user_v2(self):
        # Given
        user = users_factories.UnderageBeneficiaryFactory.create(firstName="Fabien", subscription_age=15)

        # When
        data = get_accepted_as_underage_beneficiary_email_data(user)

        # Then
        assert data.params["FIRSTNAME"] == "Fabien"
        assert data.params["CREDIT"] == 20
