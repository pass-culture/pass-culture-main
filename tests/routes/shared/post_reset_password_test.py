from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from pcapi.domain.password import RESET_PASSWORD_TOKEN_LENGTH
from pcapi.model_creators.generic_creators import create_user
from pcapi.models import UserSQLEntity
from pcapi.repository import repository

from tests.conftest import TestClient

class Returns400:
    @patch("pcapi.validation.routes.passwords.validate_recaptcha_token", return_value=True)
    def when_email_is_empty(self, validate_recaptcha_token_mock, app, db_session):
        # given
        data = {"email": "", "token": "dumbToken"}

        # when
        response = TestClient(app.test_client()).post(
            "/users/reset-password", json=data, headers={"origin": "http://localhost:3000"}
        )

        # then
        assert response.status_code == 400
        assert response.json["email"] == ["L'email renseigné est vide"]

    @patch("pcapi.validation.routes.passwords.validate_recaptcha_token", return_value=True)
    def when_email_is_missing(self, validate_recaptcha_token_mock, app, db_session):
        # given
        data = {"token": "dumbToken"}

        # when
        response = TestClient(app.test_client()).post(
            "/users/reset-password", json=data, headers={"origin": "http://localhost:3000"}
        )

        # then
        assert response.status_code == 400
        assert response.json["email"] == ["Ce champ est obligatoire"]

    def when_token_is_missing(self, app, db_session):
        # given
        data = {"email": "dumbemail"}

        # when
        response = TestClient(app.test_client()).post(
            "/users/reset-password", json=data, headers={"origin": "http://localhost:3000"}
        )

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Ce champ est obligatoire"]

    @patch("pcapi.validation.routes.passwords.validate_recaptcha_token", return_value=False)
    def when_token_is_not_valid(self, validate_recaptcha_token_mock, app, db_session):
        # given
        data = {"email": "dumbemail"}

        # when
        response = TestClient(app.test_client()).post(
            "/users/reset-password", json=data, headers={"origin": "http://localhost:3000"}
        )

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Ce champ est obligatoire"]


class Returns204:
    @patch("pcapi.validation.routes.passwords.validate_recaptcha_token", return_value=True)
    def when_user_email_is_unknown(self, validate_recaptcha_token_mock, app, db_session):
        # given
        data = {"token": "dumbToken", "email": "unknown.user@test.com"}

        # when
        response = TestClient(app.test_client()).post(
            "/users/reset-password", json=data, headers={"origin": "http://localhost:3000"}
        )

        # then
        assert response.status_code == 204

    @patch("pcapi.validation.routes.passwords.validate_recaptcha_token", return_value=True)
    def when_email_is_known(self, validate_recaptcha_token_mock, app, db_session):
        # given
        data = {"token": "dumbToken", "email": "bobby@test.com"}
        user = create_user(email="bobby@test.com")
        repository.save(user)
        user_id = user.id

        # when
        response = TestClient(app.test_client()).post(
            "/users/reset-password", json=data, headers={"origin": "http://localhost:3000"}
        )

        # then
        user = UserSQLEntity.query.get(user_id)
        assert response.status_code == 204
        assert len(user.resetPasswordToken) == RESET_PASSWORD_TOKEN_LENGTH
        now = datetime.utcnow()
        assert (now + timedelta(hours=23)) < user.resetPasswordTokenValidityLimit < (now + timedelta(hours=25))

    @patch("pcapi.validation.routes.passwords.validate_recaptcha_token", return_value=True)
    @patch("pcapi.routes.passwords.send_reset_password_email_to_user")
    @patch("pcapi.routes.passwords.send_raw_email")
    def test_should_send_reset_password_email_when_user_is_a_beneficiary(
        self,
        send_raw_email_mock,
        send_reset_password_email_to_user_mock,
        validate_recaptcha_token_mock,
        app,
        db_session,
    ):
        # given
        data = {"token": "dumbToken", "email": "bobby@example.com"}
        user = create_user(can_book_free_offers=True, email="bobby@example.com")
        app_origin_header = "http://localhost:3000"
        repository.save(user)

        # when
        TestClient(app.test_client()).post("/users/reset-password", json=data, headers={"origin": app_origin_header})

        # then
        send_reset_password_email_to_user_mock.assert_called_once_with(user, send_raw_email_mock)

    @patch("pcapi.validation.routes.passwords.validate_recaptcha_token", return_value=True)
    @patch("pcapi.routes.passwords.send_reset_password_email_to_pro")
    @patch("pcapi.routes.passwords.send_raw_email")
    def test_should_send_reset_password_email_when_user_is_an_offerer(
        self, send_raw_email_mock, send_reset_password_email_to_pro_mock, validate_recaptcha_token_mock, app, db_session
    ):
        # given
        data = {"token": "dumbToken", "email": "bobby@example.com"}
        user = create_user(can_book_free_offers=False, email="bobby@example.com")
        app_origin_header = "http://localhost:3000"
        repository.save(user)

        # when
        TestClient(app.test_client()).post("/users/reset-password", json=data, headers={"origin": app_origin_header})

        # then
        send_reset_password_email_to_pro_mock.assert_called_once_with(user, send_raw_email_mock)
