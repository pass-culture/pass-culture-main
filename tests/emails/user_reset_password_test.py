from datetime import datetime

import pytest

from pcapi.emails.user_reset_password import retrieve_data_for_reset_password_native_app_email
from pcapi.emails.user_reset_password import retrieve_data_for_reset_password_user_email
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
class MakeUserResetPasswordEmailDataTest:
    def test_email(self):
        # Given
        user = create_user(email="ewing@example.com", first_name="Bobby", reset_password_token="ABCDEFG")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        repository.save(user_offerer)

        # When
        reset_password_email_data = retrieve_data_for_reset_password_user_email(user=user)

        # Then
        assert reset_password_email_data == {
            "MJ-TemplateID": 912168,
            "MJ-TemplateLanguage": True,
            "Vars": {"prenom_user": "Bobby", "token": user.resetPasswordToken},
        }


class NativeAppUserResetPasswordEmailDataTest:
    def test_email_is_encoded_in_(self, app):
        # When
        reset_password_email_data = retrieve_data_for_reset_password_native_app_email(
            user_email="ewing+demo@example.com",
            token_value="abc",
            expiration_date=datetime(2020, 1, 1),
        )

        # Then
        assert reset_password_email_data == {
            "MJ-TemplateID": 1838526,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "native_app_link": (
                    "https://app.passculture-testing.beta.gouv.fr/native/v1/redirect_to_native/mot-de-passe-perdu"
                    "?token=abc&expiration_timestamp=1577836800&email=ewing%2Bdemo%40example.com"
                )
            },
        }
