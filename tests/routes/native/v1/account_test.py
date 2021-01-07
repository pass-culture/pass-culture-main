from datetime import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token
import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class AccountTest:
    identifier = "email@example.com"

    def test_get_user_profile_without_authentication(self, app):
        users_factories.UserFactory(email=self.identifier)

        response = TestClient(app.test_client()).get("/native/v1/me")

        assert response.status_code == 401

    def test_get_user_profile_not_found(self, app):
        users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity="other-email@example.com")
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 400
        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_get_user_profile(self, app):
        first_name = "Gaëtan"
        users_factories.UserFactory(email=self.identifier, firstName=first_name)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["email"] == self.identifier
        assert response.json["firstName"] == first_name
        assert response.json["isBeneficiary"]

    def test_get_user_profile_empty_first_name(self, app):
        first_name = ""
        users_factories.UserFactory(email=self.identifier, firstName=first_name, isBeneficiary=False)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["email"] == self.identifier
        assert response.json["firstName"] is None
        assert not response.json["isBeneficiary"]

    @patch("pcapi.routes.native.v1.account.check_recaptcha_token_is_valid")
    @patch("pcapi.utils.mailing.send_raw_email", return_value=True)
    def test_account_creation(self, mocked_send_raw_email, mocked_check_recaptcha_token_is_valid, app):
        test_client = TestClient(app.test_client())
        assert User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "hasAllowedRecommendations": True,
        }

        response = test_client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json

        user = User.query.first()
        assert user is not None
        assert user.email == "john.doe@example.com"
        assert user.isEmailValidated is False
        mocked_send_raw_email.assert_called()
        mocked_check_recaptcha_token_is_valid.assert_called()
        assert mocked_send_raw_email.call_args_list[0][1]["data"]["Mj-TemplateID"] == 1897370

    @patch("pcapi.routes.native.v1.account.check_recaptcha_token_is_valid")
    @patch("pcapi.utils.mailing.send_raw_email", return_value=True)
    def test_account_creation_with_existing_email_sends_email(
        self, mocked_send_raw_email, mocked_check_recaptcha_token_is_valid, app
    ):
        test_client = TestClient(app.test_client())
        users_factories.UserFactory(email=self.identifier)
        mocked_check_recaptcha_token_is_valid.return_value = None

        data = {
            "email": "eMail@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "hasAllowedRecommendations": True,
        }

        response = test_client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json
        mocked_send_raw_email.assert_called()
        assert mocked_send_raw_email.call_args_list[0][1]["data"]["MJ-TemplateID"] == 1838526

    @patch("pcapi.routes.native.v1.account.check_recaptcha_token_is_valid")
    def test_too_young_account_creation(self, mocked_check_recaptcha_token_is_valid, app):
        test_client = TestClient(app.test_client())
        assert User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": (datetime.utcnow() - relativedelta(year=15)).date(),
            "notifications": True,
            "token": "gnagna",
            "hasAllowedRecommendations": True,
        }

        response = test_client.post("/native/v1/account", json=data)
        assert response.status_code == 400


class ResendEmailValidationTest:
    @patch("pcapi.utils.mailing.send_raw_email", return_value=True)
    def test_resend_email_validation(self, mocked_send_raw_email, app):
        user = users_factories.UserFactory(isEmailValidated=False)

        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        mocked_send_raw_email.assert_called()
        assert mocked_send_raw_email.call_args_list[0][1]["data"]["Mj-TemplateID"] == 1897370

    @patch("pcapi.utils.mailing.send_raw_email", return_value=True)
    def test_for_already_validated_email_does_sent_passsword_reset(self, mocked_send_raw_email, app):
        user = users_factories.UserFactory(isEmailValidated=True)

        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        mocked_send_raw_email.assert_called()
        assert mocked_send_raw_email.call_args_list[0][1]["data"]["MJ-TemplateID"] == 1838526

    @patch("pcapi.utils.mailing.send_raw_email", return_value=True)
    def test_for_unknown_mail_does_nothing(self, mocked_send_raw_email, app):
        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/resend_email_validation", json={"email": "aijfioern@mlks.com"})

        assert response.status_code == 204
        mocked_send_raw_email.assert_not_called()

    @patch("pcapi.utils.mailing.send_raw_email", return_value=True)
    def test_for_deactivated_account_does_nothhing(self, mocked_send_raw_email, app):
        user = users_factories.UserFactory(isEmailValidated=True, isActive=False)

        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        mocked_send_raw_email.assert_not_called()
