from dataclasses import asdict
from datetime import datetime

import pytest

from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.reset_password import get_reset_password_email_data
from pcapi.core.mails.transactional.users.reset_password import send_reset_password_email_to_user
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendResetPasswordToUserEmailTest:
    def test_send_email(self) -> None:
        # given
        user = users_factories.UserFactory()
        token = users_factories.ResetPasswordToken(user=user)

        # when
        send_reset_password_email_to_user(user, token)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent

        reset_password_link = mails_testing.outbox[0].sent_data["params"]["RESET_PASSWORD_LINK"]
        assert user.tokens[0].value in reset_password_link
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.NEW_PASSWORD_REQUEST.value)
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["params"]["FIRSTNAME"] == user.firstName

        reset_password_link = mails_testing.outbox[0].sent_data["params"]["RESET_PASSWORD_LINK"]
        assert user.tokens[0].value in reset_password_link

    def test_get_email_metadata(self) -> None:
        # Given
        user = users_factories.UserFactory.build()
        users_factories.ResetPasswordToken.build(user=user, value="abc", expirationDate=datetime(2020, 1, 1))

        # When
        reset_password_email_data = get_reset_password_email_data(
            user, user.tokens[0], TransactionalEmail.NEW_PASSWORD_REQUEST.value
        )

        # Then
        assert reset_password_email_data.template == TransactionalEmail.NEW_PASSWORD_REQUEST.value
        assert reset_password_email_data.params["FIRSTNAME"] == user.firstName
        reset_password_link = reset_password_email_data.params["RESET_PASSWORD_LINK"]
        assert user.tokens[0].value in reset_password_link
