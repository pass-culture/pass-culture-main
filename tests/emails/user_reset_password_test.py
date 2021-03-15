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
        reset_password_email_data = retrieve_data_for_reset_password_user_email(user=user, token=user.tokens[0])

        # Then
        assert reset_password_email_data == {
            "MJ-TemplateID": 912168,
            "MJ-TemplateLanguage": True,
            "Vars": {"prenom_user": "Bobby", "token": "ABCDEFG"},
        }


class NativeAppUserResetPasswordEmailDataTest:
    def test_email_is_encoded(self, app):
        # Given
        user = create_user(
            email="ewing+demo@example.com",
            first_name="Bobby",
            reset_password_token="abc",
            reset_password_token_validity_limit=datetime(2020, 1, 1),
        )
        # When
        reset_password_email_data = retrieve_data_for_reset_password_native_app_email(user, user.tokens[0])

        # Then
        assert reset_password_email_data == {
            "MJ-TemplateID": 1838526,
            "MJ-TemplateLanguage": True,
            "Mj-trackclick": 1,
            "Vars": {
                "native_app_link": (
                    "https://app.passculture-testing.beta.gouv.fr/mot-de-passe-perdu"
                    "?token=abc&expiration_timestamp=1577836800&email=ewing%2Bdemo%40example.com"
                )
            },
        }
