from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.users import factories as user_factories
from pcapi.models.user_sql_entity import hash_password
from pcapi.repository.user_queries import find_user_by_id
from pcapi.utils.token import random_token

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def test_user_logs_in_and_refreshes_token(app):
    data = {"identifier": "user@test.com", "password": user_factories.DEFAULT_PASSWORD}
    user_factories.UserFactory(email=data["identifier"], password=data["password"])
    test_client = TestClient(app.test_client())

    # Get the refresh and access token
    response = test_client.post("/native/v1/signin", json=data)
    assert response.status_code == 200
    assert response.json["refresh_token"]
    assert response.json["access_token"]

    refresh_token = response.json["refresh_token"]
    access_token = response.json["access_token"]

    # Ensure the access token is valid
    test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
    response = test_client.get("/native/v1/protected")
    assert response.status_code == 200

    # Ensure the refresh token can generate a new access token
    test_client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
    response = test_client.post("/native/v1/refresh_access_token", json={})
    assert response.status_code == 200, response.json
    assert response.json["access_token"]
    access_token = response.json["access_token"]

    # Ensure the new access token is valid
    test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
    response = test_client.get("/native/v1/protected")
    assert response.status_code == 200


def test_user_logs_in_with_wrong_password(app):
    data = {"identifier": "user@test.com", "password": user_factories.DEFAULT_PASSWORD}
    user_factories.UserFactory(email=data["identifier"], password=data["password"])
    test_client = TestClient(app.test_client())

    # signin with invalid password and ensures the result messsage is generic
    data["password"] = data["password"][:-2]
    response = test_client.post("/native/v1/signin", json=data)
    assert response.status_code == 400
    assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}


def test_unknown_user_logs_in(app):
    data = {"identifier": "user@test.com", "password": user_factories.DEFAULT_PASSWORD}
    test_client = TestClient(app.test_client())

    # signin with invalid password and ensures the result messsage is generic
    response = test_client.post("/native/v1/signin", json=data)
    assert response.status_code == 400
    assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}


def test_user_logs_in_with_missing_fields(app):
    test_client = TestClient(app.test_client())

    response = test_client.post("/native/v1/signin", json={})
    assert response.status_code == 400
    assert response.json == {
        "identifier": ["Ce champ est obligatoire"],
        "password": ["Ce champ est obligatoire"],
    }


def test_send_reset_password_email_without_email(app):
    response = TestClient(app.test_client()).post("/native/v1/request_password_reset")

    assert response.status_code == 400
    assert response.json["email"] == ["Ce champ est obligatoire"]


def test_request_reset_password_for_unknown_email(app):
    data = {"email": "not_existing_user@example.com"}
    response = TestClient(app.test_client()).post("/native/v1/request_password_reset", json=data)

    assert response.status_code == 204


@patch("pcapi.routes.native.v1.authentication.send_reset_password_email_to_user")
def test_request_reset_password_for_existing_email(mock_send_reset_password_email_to_user, app):
    email = "existing_user@example.com"
    data = {"email": email}
    user = user_factories.UserFactory(email=email)

    assert user.resetPasswordToken is None

    mock_send_reset_password_email_to_user.return_value = True

    response = TestClient(app.test_client()).post("/native/v1/request_password_reset", json=data)

    mock_send_reset_password_email_to_user.assert_called_once()
    assert response.status_code == 204
    assert user.resetPasswordToken is not None


@pytest.mark.usefixtures("db_session")
@patch("pcapi.routes.native.v1.authentication.send_reset_password_email_to_user")
def test_request_reset_password_with_mail_service_exception(mock_send_reset_password_email_to_user, app):
    email = "existing_user@example.com"
    data = {"email": email}
    user_factories.UserFactory(email=email)

    mock_send_reset_password_email_to_user.return_value = False

    response = TestClient(app.test_client()).post("/native/v1/request_password_reset", json=data)

    mock_send_reset_password_email_to_user.assert_called_once()
    assert response.status_code == 400
    assert response.json["email"] == ["L'email n'a pas pu être envoyé"]


def test_reset_password_with_unfound_token(app):
    data = {"reset_password_token": "unknwon_token", "new_password": "new_password"}
    user = user_factories.UserFactory()
    old_password = user.password

    response = TestClient(app.test_client()).post("/native/v1/reset_password", json=data)

    assert response.status_code == 400
    assert user.password == old_password


def test_reset_password_success(app):
    reset_token = random_token()
    new_password = "New_password1998!"

    user = user_factories.UserFactory(
        resetPasswordToken=reset_token,
        resetPasswordTokenValidityLimit=(datetime.utcnow() + timedelta(hours=1)),
    )

    data = {"reset_password_token": reset_token, "new_password": new_password}
    response = TestClient(app.test_client()).post("/native/v1/reset_password", json=data)

    user = find_user_by_id(user.id)
    assert response.status_code == 204
    assert user.password == hash_password(new_password)


def test_reset_password_fail_for_token_validity(app):
    reset_token = random_token()
    user = user_factories.UserFactory(
        resetPasswordToken=reset_token,
        resetPasswordTokenValidityLimit=(datetime.utcnow() - timedelta(hours=1)),
    )
    new_password = "New_password1998!"
    old_password = user.password

    data = {"reset_password_token": reset_token, "new_password": new_password}
    response = TestClient(app.test_client()).post("/native/v1/reset_password", json=data)

    user = find_user_by_id(user.id)
    assert response.status_code == 400
    assert user.password == old_password


def test_reset_password_fail_for_password_strenght(app):
    reset_token = random_token()
    user = user_factories.UserFactory(
        resetPasswordToken=reset_token,
        resetPasswordTokenValidityLimit=(datetime.utcnow() + timedelta(hours=1)),
    )
    old_password = user.password
    new_password = "weak_password"

    data = {"reset_password_token": reset_token, "new_password": new_password}

    response = TestClient(app.test_client()).post("/native/v1/reset_password", json=data)

    user = find_user_by_id(user.id)
    assert response.status_code == 400
    assert user.password == old_password
