from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models
from pcapi.core.users import testing as users_testing
from pcapi.core.users.models import TokenType
from pcapi.notifications.push import testing as push_testing


@pytest.mark.usefixtures("db_session")
def test_change_password(client):
    user = users_factories.UserFactory()
    token = users_factories.TokenFactory(user=user, type=TokenType.RESET_PASSWORD)
    data = {"token": token.value, "newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 204
    assert user.checkPassword("N3W_p4ssw0rd")

    assert len(user.tokens) == 1
    token = models.Token.query.get(token.id)
    assert token.isUsed


@pytest.mark.usefixtures("db_session")
def test_change_password_validates_email(client):
    user = users_factories.UserFactory(isEmailValidated=False)
    token = users_factories.TokenFactory(user=user, type=TokenType.RESET_PASSWORD)
    data = {"token": token.value, "newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 204
    assert user.checkPassword("N3W_p4ssw0rd")
    assert len(user.tokens) == 1
    token = models.Token.query.get(token.id)
    assert token.isUsed

    # One call should be sent to batch, and one to sendinblue
    assert len(push_testing.requests) == 2
    assert len(users_testing.sendinblue_requests) == 1
    sendinblue_data = users_testing.sendinblue_requests[0]
    assert sendinblue_data["attributes"]["IS_EMAIL_VALIDATED"]


@pytest.mark.usefixtures("db_session")
def test_fail_if_token_has_expired(client):
    user = users_factories.UserFactory(password="Old_P4ssword")
    token = users_factories.TokenFactory(
        userId=user.id,
        type=TokenType.RESET_PASSWORD,
        expirationDate=datetime.utcnow() - timedelta(hours=24),
    )
    data = {"token": token.value, "newPassword": "N3W_p4ssw0rd"}

    response = client.post("/users/new-password", json=data)

    assert response.status_code == 400
    assert response.json["token"] == ["Votre lien de changement de mot de passe est invalide."]
    assert user.checkPassword("Old_P4ssword")


@pytest.mark.usefixtures("db_session")
def test_fail_if_token_is_unknown(client):
    user = users_factories.UserFactory()
    users_factories.TokenFactory(user=user, type=TokenType.RESET_PASSWORD, value="ONE TOKEN")
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
        "Ton mot de passe doit contenir au moins :\n"
        "- 12 caractères\n"
        "- Un chiffre\n"
        "- Une majuscule et une minuscule\n"
        "- Un caractère spécial"
    ]
