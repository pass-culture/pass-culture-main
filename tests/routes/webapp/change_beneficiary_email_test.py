from unittest.mock import call
from unittest.mock import patch

from freezegun import freeze_time
import pytest

import pcapi.core.users.factories as users_factories
from pcapi.settings import WEBAPP_URL

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns204:
    @patch("pcapi.core.users.api.mailing_utils")
    @freeze_time("2020-10-15 09:00:00")
    def when_account_is_known(self, mocked_mailing_utils, app):
        # given
        mocked_mailing_utils.send_raw_email.return_value = True

        user = users_factories.UserFactory(email="test@mail.com")
        data = {"new_email": "new@email.com", "password": "user@AZERTY123"}

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # then
        assert response.status_code == 204
        information_data = {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 2066067,
            "MJ-TemplateLanguage": True,
            "To": user.email,
            "Vars": {"beneficiary_name": user.firstName},
        }
        confirmation_data_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjdXJyZW50X2VtYWlsIjo"
            "idGVzdEBtYWlsLmNvbSIsIm5ld19lbWFpbCI6Im5ld0BlbWFpbC5jb20iLCJ"
            "leHAiOjE2MDI4Mzg4MDB9.Q2-583JqPSfDjuMD6ZMhMnb07Rr47iBZFRwlFC"
            "ymSf0"
        )
        confirmation_link = f"{WEBAPP_URL}/email-change?token={confirmation_data_token}&expiration_timestamp=1602838800"
        confirmation_data = {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 2066065,
            "MJ-TemplateLanguage": True,
            "To": "new@email.com",
            "Vars": {
                "beneficiary_name": "Jeanne",
                "confirmation_link": confirmation_link,
            },
        }

        assert mocked_mailing_utils.send_raw_email.call_count == 2
        calls = [call(information_data), call(confirmation_data)]
        mocked_mailing_utils.send_raw_email.assert_has_calls(calls)


@pytest.mark.usefixtures("db_session")
class Returns400:
    def when_password_is_missing(self, app):
        # Given
        user = users_factories.UserFactory()
        data = {"new_email": "toto"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["password"] == ["Ce champ est obligatoire"]

    def when_new_email_is_missing(self, app):
        # Given
        user = users_factories.UserFactory()
        data = {"password": "user@AZERTY123"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["new_email"] == ["Ce champ est obligatoire"]


@pytest.mark.usefixtures("db_session")
class Returns401:
    def when_password_is_incorrect(self, app):
        # Given
        user = users_factories.UserFactory()
        data = {"new_email": "new email", "password": "wrong password"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["password"] == ["Mot de passe incorrect"]

    def when_account_is_not_active(self, app):
        # Given
        user = users_factories.UserFactory(isActive=False)
        data = {"new_email": user.email, "password": "user@AZERTY123"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant incorrect"]

    def when_account_is_not_validated(self, app):
        # Given
        user = users_factories.UserFactory()
        user.generate_validation_token()
        data = {"new_email": user.email, "password": "user@AZERTY123"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Ce compte n'est pas validé."]
