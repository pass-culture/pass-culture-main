from dataclasses import asdict
from datetime import datetime

import pytest

from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.reset_password import get_reset_password_native_app_email_data
from pcapi.core.mails.transactional.users.reset_password import get_reset_password_user_email_data
from pcapi.core.mails.transactional.users.reset_password import send_reset_password_email_to_native_app_user
from pcapi.core.mails.transactional.users.reset_password import send_reset_password_email_to_user
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository


pytestmark = pytest.mark.usefixtures("db_session")


class MailjetSendResetPasswordUserEmailTest:
    def test_email(self) -> None:
        # Given
        user = users_factories.UserFactory(email="ewing@example.com", firstName="Bobby")
        users_factories.ResetPasswordToken(user=user, value="ABCDEFG")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        repository.save(user_offerer)

        # When
        reset_password_email_data = get_reset_password_user_email_data(user=user, token=user.tokens[0])

        # Then
        assert reset_password_email_data == {
            "MJ-TemplateID": 912168,
            "MJ-TemplateLanguage": True,
            "Vars": {"prenom_user": "Bobby", "token": "ABCDEFG"},
        }

    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_user(self) -> None:
        # given
        user = users_factories.UserFactory(email="bobby@example.com")

        # when
        send_reset_password_email_to_user(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 912168


class SendinblueSendResetPasswordUserEmailTest:
    def test_send_a_reset_password_email_to_native_app_user_via_sendinblue(self) -> None:
        # given
        user = users_factories.UserFactory(email="bobby@example.com")

        # when
        send_reset_password_email_to_native_app_user(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent

        native_app_link = mails_testing.outbox[0].sent_data["params"]["NATIVE_APP_LINK"]
        assert user.tokens[0].value in native_app_link
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.NEW_PASSWORD_REQUEST.value)
        assert mails_testing.outbox[0].sent_data["To"] == user.email

    def test_native_app_email(self) -> None:
        # Given
        user = users_factories.UserFactory.build(
            email="ewing+demo@example.com",
            firstName="Bobby",
        )
        users_factories.ResetPasswordToken.build(user=user, value="abc", expirationDate=datetime(2020, 1, 1))
        # When
        reset_password_email_data = get_reset_password_native_app_email_data(user, user.tokens[0])

        # Then
        native_app_link = reset_password_email_data.params["NATIVE_APP_LINK"]
        assert user.tokens[0].value in native_app_link
        assert reset_password_email_data.template == TransactionalEmail.NEW_PASSWORD_REQUEST.value
