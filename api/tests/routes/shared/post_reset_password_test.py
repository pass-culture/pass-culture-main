from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from pcapi.connectors.api_recaptcha import InvalidRecaptchaTokenException
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User

from tests.conftest import TestClient


class Returns400Test:
    @patch("pcapi.routes.shared.passwords.check_webapp_recaptcha_token", return_value=None)
    def when_email_is_empty(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"email": "", "token": "dumbToken"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["email"] == ["L'email renseigné est vide"]

    @patch("pcapi.routes.shared.passwords.check_webapp_recaptcha_token", return_value=None)
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

    @patch("pcapi.routes.shared.passwords.check_webapp_recaptcha_token", return_value=None)
    def when_token_is_not_sent(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"email": "dumbemail"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Ce champ est obligatoire"]

    @patch("pcapi.routes.shared.passwords.check_webapp_recaptcha_token", side_effect=InvalidRecaptchaTokenException())
    def when_token_is_wrong_or_already_used(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"email": "dumbemail", "token": "dumbToken"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Le token renseigné n'est pas valide"]


class Returns204Test:
    @patch("pcapi.routes.shared.passwords.check_webapp_recaptcha_token", return_value=None)
    def when_user_email_is_unknown(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        data = {"token": "dumbToken", "email": "unknown.user@test.com"}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204

    @patch("pcapi.routes.shared.passwords.check_webapp_recaptcha_token", return_value=None)
    def when_account_is_not_valid(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        user = users_factories.UserFactory(isActive=False)
        data = {"token": "dumbToken", "email": user.email}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204
        user = User.query.get(user.id)

    @patch("pcapi.routes.shared.passwords.check_webapp_recaptcha_token", return_value=None)
    def when_email_is_known(self, check_recaptcha_token_is_valid_mock, app, db_session):
        # given
        user = users_factories.UserFactory()
        data = {"token": "dumbToken", "email": user.email}

        # when
        response = TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204
        user = User.query.get(user.id)
        assert len(user.tokens) == 1
        now = datetime.utcnow()
        assert (now + timedelta(hours=23)) < user.tokens[0].expirationDate < (now + timedelta(hours=25))

    @patch("pcapi.routes.shared.passwords.check_webapp_recaptcha_token", return_value=None)
    @patch("pcapi.routes.shared.passwords.send_reset_password_email_to_pro")
    def test_should_send_reset_password_email_when_user_is_a_pro(
        self,
        send_reset_password_email_to_pro_mock,
        check_recaptcha_token_is_valid_mock,
        app,
        db_session,
    ):
        # given
        pro = users_factories.ProFactory()
        data = {"token": "dumbToken", "email": pro.email}

        # when
        TestClient(app.test_client()).post("/users/reset-password", json=data)

        # then
        send_reset_password_email_to_pro_mock.assert_called_once_with(pro)
