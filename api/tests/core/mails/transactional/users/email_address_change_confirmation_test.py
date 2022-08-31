import pytest

from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_address_change_confirmation import get_email_confirmation_email_data
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueAddressEmailChangeConfirmationTest:
    def test_should_return_sendinblue_data_when_feature_toggled(self):
        # Given
        user = users_factories.UserFactory.create(email="fabien+test@example.net", firstName="Fabien")
        users_factories.PasswordResetTokenFactory(user=user, value="ABCD123")

        # When
        activation_email_data = get_email_confirmation_email_data(user, user.tokens[0])

        # Then
        assert activation_email_data.template == TransactionalEmail.EMAIL_CONFIRMATION.value
        assert activation_email_data.params["CONFIRMATION_LINK"]
        assert "email%3Dfabien%252Btest%2540example.net" in activation_email_data.params["CONFIRMATION_LINK"]
