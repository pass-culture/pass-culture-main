import pytest

from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_address_change import get_confirmation_email_change_data
from pcapi.core.mails.transactional.users.email_address_change import get_validation_email_change_data
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueEmailAddressChangeTest:
    def test_should_return_sendinblue_confirmation_data(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")
        confirmation_link = "http://example.com/confirmation"
        cancellation_link = "http://example.com/cancellation"

        # When
        data = get_confirmation_email_change_data(user.firstName, confirmation_link, cancellation_link)

        # Then
        assert data.template == TransactionalEmail.EMAIL_CHANGE_REQUEST.value
        assert data.params["FIRSTNAME"] == "Fabien"
        assert data.params["EXPIRATION_DELAY"] == 24
        assert data.params["CONFIRMATION_LINK"] == confirmation_link
        assert data.params["CANCELLATION_LINK"] == cancellation_link

    def test_should_return_sendinblue_validation_data(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")
        users_factories.PasswordResetTokenFactory(user=user, value="ABCD123")

        # When
        data = get_validation_email_change_data(first_name=user.firstName, confirmation_link="ABCD123")

        # Then
        assert data.template == TransactionalEmail.EMAIL_CHANGE_CONFIRMATION.value
        assert data.params["FIRSTNAME"] == "Fabien"
        assert data.params["CONFIRMATION_LINK"] == "ABCD123"
