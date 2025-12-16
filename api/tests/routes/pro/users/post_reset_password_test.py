from datetime import timedelta
from unittest.mock import patch

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.connectors.api_recaptcha import InvalidRecaptchaTokenException
from pcapi.core import token as token_utils
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils import date as date_utils


class Returns400Test:
    def _get_base_payload(self) -> dict:
        return {"email": "dumbemail@coucou.com", "token": "coucou"}

    @pytest.mark.parametrize(
        "partial_json,expected_response",
        [
            ({"email": ""}, {"email": ["Saisissez un email valide"]}),
            ({"token": ""}, {"token": ["Cette chaîne de caractères doit avoir une taille minimum de 1 caractères"]}),
            ({"email": None}, {"email": ["Saisissez une chaîne de caractères valide"]}),
            ({"token": None}, {"token": ["Saisissez une chaîne de caractères valide"]}),
        ],
    )
    def when_data_is_invalid(self, partial_json, expected_response, client):
        data = self._get_base_payload()
        data.update(**partial_json)

        response = client.post("/users/reset-password", json=data)

        assert response.status_code == 400
        assert response.json == expected_response

    @pytest.mark.parametrize("missing_field", ("email", "token"))
    def when_data_is_missing(self, missing_field, client):
        data = self._get_base_payload()
        data.pop(missing_field)

        response = client.post("/users/reset-password", json=data)

        assert response.status_code == 400
        assert response.json == {missing_field: ["Ce champ est obligatoire"]}

    @patch("pcapi.routes.pro.users.check_web_recaptcha_token", side_effect=InvalidRecaptchaTokenException())
    def when_token_is_wrong_or_already_used(self, check_recaptcha_token_is_valid_mock, client):
        data = {"email": "dumbemail@coucou.com", "token": "dumbToken"}

        response = client.post("/users/reset-password", json=data)

        assert response.status_code == 400
        assert response.json["token"] == ["Le token renseigné n'est pas valide"]


class Returns204Test:
    @patch("pcapi.routes.pro.users.check_web_recaptcha_token", return_value=None)
    def when_user_email_is_unknown(self, check_recaptcha_token_is_valid_mock, client):
        data = {"token": "dumbToken", "email": "unknown.user@test.com"}

        response = client.post("/users/reset-password", json=data)

        assert response.status_code == 204

    @patch("pcapi.routes.pro.users.check_web_recaptcha_token", return_value=None)
    def when_account_is_not_valid(self, check_recaptcha_token_is_valid_mock, client):
        user = users_factories.UserFactory(isActive=False)
        data = {"token": "dumbToken", "email": user.email}

        response = client.post("/users/reset-password", json=data)

        assert response.status_code == 204
        user = db.session.get(User, user.id)

    @patch("pcapi.routes.pro.users.check_web_recaptcha_token", return_value=None)
    def when_email_is_known(self, check_recaptcha_token_is_valid_mock, client):
        user = users_factories.UserFactory()
        data = {"token": "dumbToken", "email": user.email}

        response = client.post("/users/reset-password", json=data)

        assert response.status_code == 204
        user = db.session.get(User, user.id)
        assert token_utils.Token.token_exists(token_utils.TokenType.RESET_PASSWORD, user.id)
        now = date_utils.get_naive_utc_now()
        assert (
            (now + timedelta(hours=23))
            < token_utils.Token.get_expiration_date(token_utils.TokenType.RESET_PASSWORD, user.id)
            < (now + timedelta(hours=25))
        )

    @patch("pcapi.routes.pro.users.check_web_recaptcha_token", return_value=None)
    def test_should_send_reset_password_email_when_user_is_a_pro(self, check_recaptcha_token_is_valid_mock, client):
        pro = users_factories.ProFactory()
        data = {"token": "dumbToken", "email": pro.email}

        client.post("/users/reset-password", json=data)

        assert len(mails_testing.outbox) == 1
