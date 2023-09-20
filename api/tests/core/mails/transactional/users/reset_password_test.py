from dataclasses import asdict

import pytest

from pcapi.core import token as token_utils
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.reset_password import get_reset_password_email_data
from pcapi.core.mails.transactional.users.reset_password import send_reset_password_email_to_user
from pcapi.core.users import constants
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendResetPasswordToUserEmailTest:
    def test_send_email(self) -> None:
        # given
        user = users_factories.UserFactory()
        token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
        )

        # when
        send_reset_password_email_to_user(token)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent

        reset_password_link = mails_testing.outbox[0].sent_data["params"]["RESET_PASSWORD_LINK"]
        assert token.encoded_token in reset_password_link
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.NEW_PASSWORD_REQUEST.value)
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["params"]["FIRSTNAME"] == user.firstName

    def test_get_email_metadata(self) -> None:
        # Given
        user = users_factories.UserFactory.build()
        token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
        )
        # When
        reset_password_email_data = get_reset_password_email_data(
            user, token, TransactionalEmail.NEW_PASSWORD_REQUEST.value
        )

        # Then
        assert reset_password_email_data.template == TransactionalEmail.NEW_PASSWORD_REQUEST.value
        assert reset_password_email_data.params["FIRSTNAME"] == user.firstName
        reset_password_link = reset_password_email_data.params["RESET_PASSWORD_LINK"]
        assert token.encoded_token in reset_password_link
