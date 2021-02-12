from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from pcapi.connectors.api_recaptcha import InvalidRecaptchaTokenException
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.domain.password import RESET_PASSWORD_TOKEN_LENGTH

from tests.conftest import TestClient


class Returns400:
    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", return_value=True)
    def when_email_is_empty(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"email": "", "token": "dumbToken"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["email"] == ["L'email renseigné est vide"]

    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", return_value=True)
    def when_email_is_missing(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"token": "dumbToken"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["email"] == ["Ce champ est obligatoire"]

    def when_token_is_missing(self, app, db_session):
        # given
        data = {"email": "dumbemail"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Ce champ est obligatoire"]

    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", return_value=False)
    def when_token_is_not_sent(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"email": "dumbemail"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Ce champ est obligatoire"]

    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", side_effect=InvalidRecaptchaTokenException())
    def when_token_is_wrong_or_already_used(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"email": "dumbemail", "token": "dumbToken"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Le token renseigné n'est pas valide"]


class Returns204:
    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", return_value=True)
    def when_user_email_is_unknown(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"token": "dumbToken", "email": "unknown.user@test.com"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204

    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", return_value=True)
    def when_account_is_not_valid(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        user = users_factories.UserFactory(isActive=False)
        data = {"token": "dumbToken", "email": user.email}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204
        user = User.query.get(user.id)
        assert not user.resetPasswordToken

    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", return_value=True)
    def when_email_is_known(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        user = users_factories.UserFactory()
        data = {"token": "dumbToken", "email": user.email}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204
        user = User.query.get(user.id)
        assert len(user.resetPasswordToken) == RESET_PASSWORD_TOKEN_LENGTH
        now = datetime.utcnow()
        assert (now + timedelta(hours=23)) < user.resetPasswordTokenValidityLimit < (now + timedelta(hours=25))

    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", return_value=True)
    @patch("pcapi.routes.shared.passwords.send_reset_password_email_to_user")
    def test_should_send_reset_password_email_when_user_is_a_beneficiary(
        self,
        send_reset_password_email_to_user_mock,
        check_recaptcha_token_is_valid_mock,
        app,
        db_session,
    ):
        # given
        user = users_factories.UserFactory()
        data = {"token": "dumbToken", "email": user.email}

        # when
        TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        send_reset_password_email_to_user_mock.assert_called_once_with(user)

    @patch("pcapi.routes.shared.passwords.check_recaptcha_token_is_valid", return_value=True)
    @patch("pcapi.routes.shared.passwords.send_reset_password_email_to_pro")
    def test_should_send_reset_password_email_when_user_is_an_offerer(
        self,
        send_reset_password_email_to_pro_mock,
        check_recaptcha_token_is_valid_mock,
        app,
        db_session,
    ):
        # given
        user = users_factories.UserFactory(isBeneficiary=False)
        data = {"token": "dumbToken", "email": user.email}

        # when
        TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        send_reset_password_email_to_pro_mock.assert_called_once_with(user)
