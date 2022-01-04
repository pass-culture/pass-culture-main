import pytest

from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_address_change_confirmation import get_email_confirmation_email_data
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueAddressEmailChangeConfirmationTest:
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
