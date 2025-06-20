from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.connectors.api_recaptcha import InvalidRecaptchaTokenException
from pcapi.core import token as token_utils
from pcapi.core.users.models import User
from pcapi.models import db


class Returns400Test:
    @patch("pcapi.routes.shared.passwords.check_web_recaptcha_token", return_value=None)
    def when_email_is_empty(self, check_recaptcha_token_is_valid_mock, client, db_session):
        # given
        data = {"email": "", "token": "dumbToken"}

        # when
        response = client.post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["email"] == ["L'email renseigné est vide"]

    @patch("pcapi.routes.shared.passwords.check_web_recaptcha_token", return_value=None)
    def when_email_is_missing(self, check_recaptcha_token_is_valid_mock, client, db_session):
        # given
        data = {"token": "dumbToken"}

        # when
        response = client.post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["email"] == ["Ce champ est obligatoire"]

    def when_token_is_missing(self, client, db_session):
        # given
        data = {"email": "dumbemail"}

        # when
        response = client.post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Ce champ est obligatoire"]

    @patch("pcapi.routes.shared.passwords.check_web_recaptcha_token", return_value=None)
    def when_token_is_not_sent(self, check_recaptcha_token_is_valid_mock, client, db_session):
        # given
        data = {"email": "dumbemail"}

        # when
        response = client.post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Ce champ est obligatoire"]

    @patch("pcapi.routes.shared.passwords.check_web_recaptcha_token", side_effect=InvalidRecaptchaTokenException())
    def when_token_is_wrong_or_already_used(self, check_recaptcha_token_is_valid_mock, client, db_session):
        # given
        data = {"email": "dumbemail", "token": "dumbToken"}

        # when
        response = client.post("/users/reset-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["token"] == ["Le token renseigné n'est pas valide"]


class Returns204Test:
    @patch("pcapi.routes.shared.passwords.check_web_recaptcha_token", return_value=None)
    def when_user_email_is_unknown(self, check_recaptcha_token_is_valid_mock, client, db_session):
        # given
        data = {"token": "dumbToken", "email": "unknown.user@test.com"}

        # when
        response = client.post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204

    @patch("pcapi.routes.shared.passwords.check_web_recaptcha_token", return_value=None)
    def when_account_is_not_valid(self, check_recaptcha_token_is_valid_mock, client, db_session):
        # given
        user = users_factories.UserFactory(isActive=False)
        data = {"token": "dumbToken", "email": user.email}

        # when
        response = client.post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204
        user = db.session.get(User, user.id)

    @patch("pcapi.routes.shared.passwords.check_web_recaptcha_token", return_value=None)
    def when_email_is_known(self, check_recaptcha_token_is_valid_mock, client, db_session):
        # given
        user = users_factories.UserFactory()
        data = {"token": "dumbToken", "email": user.email}

        # when
        response = client.post("/users/reset-password", json=data)

        # then
        assert response.status_code == 204
        user = db.session.get(User, user.id)
        assert token_utils.Token.token_exists(token_utils.TokenType.RESET_PASSWORD, user.id)
        now = datetime.utcnow()
        assert (
            (now + timedelta(hours=23))
            < token_utils.Token.get_expiration_date(token_utils.TokenType.RESET_PASSWORD, user.id)
            < (now + timedelta(hours=25))
        )

    @patch("pcapi.routes.shared.passwords.check_web_recaptcha_token", return_value=None)
    def test_should_send_reset_password_email_when_user_is_a_pro(
        self,
        check_recaptcha_token_is_valid_mock,
        client,
        db_session,
    ):
        # given
        pro = users_factories.ProFactory()
        data = {"token": "dumbToken", "email": pro.email}

        # when
        client.post("/users/reset-password", json=data)

        # then
        assert len(mails_testing.outbox) == 1
