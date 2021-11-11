from datetime import datetime

import pytest

from pcapi.core.mails.transactional import users as user_emails
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
class MakeUserResetPasswordEmailDataTest:
    def test_email(self):
        # Given
        user = users_factories.UserFactory(email="ewing@example.com", firstName="Bobby")
        users_factories.ResetPasswordToken(user=user, value="ABCDEFG")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        repository.save(user_offerer)

        # When
        reset_password_email_data = user_emails.retrieve_data_for_reset_password_user_email(
            user=user, token=user.tokens[0]
        )

        # Then
        assert reset_password_email_data == {
            "MJ-TemplateID": 912168,
            "MJ-TemplateLanguage": True,
            "Vars": {"prenom_user": "Bobby", "token": "ABCDEFG"},
        }


class NativeAppUserResetPasswordEmailDataTest:
    def test_email_is_encoded(self, app):
        # Given
        user = users_factories.UserFactory.build(
            email="ewing+demo@example.com",
            firstName="Bobby",
        )
        users_factories.ResetPasswordToken.build(user=user, value="abc", expirationDate=datetime(2020, 1, 1))
        # When
        reset_password_email_data = user_emails.retrieve_data_for_reset_password_native_app_email(user, user.tokens[0])

        # Then
        assert reset_password_email_data == {
            "MJ-TemplateID": 1838526,
            "MJ-TemplateLanguage": True,
            "Mj-trackclick": 1,
            "Vars": {
                "native_app_link": (
                    "https://passcultureapptestauto.page.link/"
                    "?link=https%3A%2F%2Fapp-native.testing.internal-passculture.app%2Fmot-de-passe-perdu%3F"
                    "token%3Dabc%26expiration_timestamp%3D1577836800%26email%3Dewing%252Bdemo%2540example.com"
                )
            },
        }
