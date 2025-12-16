from unittest import mock

import fakeredis
import pytest
import time_machine

from pcapi.core import token as token_utils
from pcapi.core.users import constants as user_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as users_testing
from pcapi.notifications.push import testing as push_testing


@pytest.mark.usefixtures("db_session")
def test_change_password(client):
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


@pytest.mark.usefixtures("db_session")
def test_change_password_validates_email(client):
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

    # One call should be sent to batch, and one to sendinblue
    assert len(push_testing.requests) == 2
    assert len(users_testing.sendinblue_requests) == 1
    sendinblue_data = users_testing.sendinblue_requests[0]
    assert sendinblue_data["attributes"]["IS_EMAIL_VALIDATED"]


@pytest.mark.usefixtures("db_session")
def test_fail_if_token_has_expired(client):
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


@pytest.mark.usefixtures("db_session")
def test_fail_if_token_is_unknown(client):
    user = users_factories.UserFactory()
    token_utils.Token.create(
        token_utils.TokenType.RESET_PASSWORD, user_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
    )
    data = {"token": "OTHER TOKEN", "newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["token"] == ["Votre lien de changement de mot de passe est invalide."]


def test_fail_if_token_is_missing(client):
    data = {"newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["token"] == ["Ce champ est obligatoire"]


@pytest.mark.usefixtures("db_session")
def test_fail_if_new_password_is_missing(client):
    data = {"token": "KL89PBNG51"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["newPassword"] == ["Ce champ est obligatoire"]


@pytest.mark.usefixtures("db_session")
def test_fail_if_new_password_is_not_strong_enough(client):
    data = {"token": "TOKEN", "newPassword": "weak_password"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["newPassword"] == [
        "Le mot de passe doit contenir au moins :\n"
        "- Entre 12 et 72 caractères\n"
        "- Un chiffre\n"
        "- Une majuscule et une minuscule\n"
        "- Un caractère spécial"
    ]
