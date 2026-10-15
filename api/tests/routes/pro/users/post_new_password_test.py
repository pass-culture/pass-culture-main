from unittest import mock

import fakeredis
import pytest
import time_machine

from pcapi.core import token as token_utils
from pcapi.core.external.batch import testing as push_testing
from pcapi.core.users import constants as user_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as users_testing
from pcapi.core.users.models import UserSession
from pcapi.models import db

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def test_change_password(client: TestClient):
    user = users_factories.UserFactory()
    token = token_utils.Token.create(
        token_utils.TokenType.RESET_PASSWORD, user_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
    )
    data = {"token": token.encoded_token, "newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 204
    assert user.checkPassword("N3W_p4ssw0rd")
    with pytest.raises(users_exceptions.InvalidToken):
        token.check(token_utils.TokenType.RESET_PASSWORD)


def test_change_password_validates_email(client: TestClient):
    user = users_factories.UserFactory(isEmailValidated=False)
    token = token_utils.Token.create(
        token_utils.TokenType.RESET_PASSWORD, user_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
    )
    data = {"token": token.encoded_token, "newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 204
    assert user.checkPassword("N3W_p4ssw0rd")
    with pytest.raises(users_exceptions.InvalidToken):
        token.check(token_utils.TokenType.RESET_PASSWORD)

    # One call should be sent to batch, and one to Brevo
    assert len(push_testing.requests) == 2
    assert len(users_testing.brevo_requests) == 1
    brevo_data = users_testing.brevo_requests[0]
    assert brevo_data["attributes"]["IS_EMAIL_VALIDATED"]


def test_fail_if_token_has_expired(client: TestClient):
    with mock.patch("flask.current_app.redis_client", fakeredis.FakeStrictRedis()):
        with time_machine.travel("2021-10-15 12:48:00"):
            user = users_factories.UserFactory(password="Old_P4ssword")
            token = token_utils.Token.create(
                token_utils.TokenType.RESET_PASSWORD, user_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
            )
            data = {"token": token.encoded_token, "newPassword": "N3W_p4ssw0rd"}
        with time_machine.travel("2021-10-25 12:48:00"):
            response = client.post("/users/new-password", json=data)

            assert response.status_code == 400
            assert response.json["token"] == ["Votre lien de changement de mot de passe est invalide."]
            assert user.checkPassword("Old_P4ssword")


def test_fail_if_token_is_unknown(client: TestClient):
    user = users_factories.UserFactory()
    token_utils.Token.create(
        token_utils.TokenType.RESET_PASSWORD, user_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
    )
    data = {"token": "OTHER TOKEN", "newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["token"] == ["Votre lien de changement de mot de passe est invalide."]


def test_fail_if_token_is_missing(client: TestClient):
    data = {"newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["token"] == ["Ce champ est obligatoire"]


def test_fail_if_new_password_is_missing(client: TestClient):
    data = {"token": "KL89PBNG51"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["newPassword"] == ["Ce champ est obligatoire"]


def test_fail_if_new_password_is_not_strong_enough(client: TestClient):
    data = {"token": "TOKEN", "newPassword": "weak_password"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["newPassword"] == [
        (
            "Le mot de passe doit contenir au moins :\n"
            "- Entre 12 et 72 caractères\n"
            "- Un chiffre\n"
            "- Une majuscule et une minuscule\n"
            "- Un caractère spécial"
        )
    ]


def test_pro_account_remove_session(client: TestClient):
    user = users_factories.ProFactory()
    assert db.session.query(UserSession).filter(UserSession.userId == user.id).count() == 0

    data = {"identifier": user.email, "password": user.clearTextPassword, "captchaToken": "token"}
    response = client.post("/users/signin", json=data)

    assert response.status_code == 200
    assert db.session.query(UserSession).filter(UserSession.userId == user.id).count() == 1

    token = token_utils.Token.create(
        token_utils.TokenType.RESET_PASSWORD, user_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
    )

    data = {"token": token.encoded_token, "newPassword": "N3W_p4ssw0rd"}
    response = client.post("/users/new-password", json=data)

    assert response.status_code == 204
    assert db.session.query(UserSession).filter(UserSession.userId == user.id).count() == 0
