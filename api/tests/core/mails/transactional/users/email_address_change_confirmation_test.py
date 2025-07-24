import pytest

import pcapi.core.users.constants as users_constants
from pcapi.core import token as token_utils
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_address_change_confirmation import get_email_confirmation_email_data
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueAddressEmailChangeConfirmationTest:
    def test_should_return_sendinblue_data_when_feature_toggled(self):
        # Given
        user = users_factories.UserFactory.create(email="fabien+test@example.net")
        token = token_utils.Token.create(
            type_=token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
            ttl=users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
            user_id=user.id,
        )

        # When
        activation_email_data = get_email_confirmation_email_data(user.email, token)

        # Then
        assert activation_email_data.template == TransactionalEmail.EMAIL_CONFIRMATION.value
        assert activation_email_data.params["CONFIRMATION_LINK"]
        assert "email=fabien%2Btest%40example.net" in activation_email_data.params["CONFIRMATION_LINK"]
