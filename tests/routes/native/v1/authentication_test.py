from datetime import datetime
from unittest.mock import patch

from flask_jwt_extended import decode_token
from flask_jwt_extended.utils import create_access_token
from freezegun import freeze_time
import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.models import db
import pcapi.notifications.push.testing as bash_testing
from pcapi.utils import crypto


pytestmark = pytest.mark.usefixtures("db_session")


def test_user_logs_in_and_refreshes_token(client):
    data = {"identifier": "user@test.com", "password": users_factories.DEFAULT_PASSWORD}
    user = users_factories.UserFactory(email=data["identifier"], password=data["password"])

    # Get the refresh and access token
    response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 200
    assert response.json["refreshToken"]
    assert response.json["accessToken"]

    refresh_token = response.json["refreshToken"]
    access_token = response.json["accessToken"]

    # Ensure the access token is valid
    client.auth_header = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/native/v1/me")
    assert response.status_code == 200

    # Ensure the access token contains user.id
    decoded = decode_token(access_token)
    assert decoded["user_claims"]["user_id"] == user.id

    # Ensure the refresh token can generate a new access token
    client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post("/native/v1/refresh_access_token", json={})
    assert response.status_code == 200, response.json
    assert response.json["accessToken"]
    access_token = response.json["accessToken"]

    # Ensure the new access token is valid
    client.auth_header = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/native/v1/me")
    assert response.status_code == 200

    # Ensure the new access token contains user.id
    decoded = decode_token(access_token)
    assert decoded["user_claims"]["user_id"] == user.id


def test_user_logs_in_with_wrong_password(client):
    data = {"identifier": "user@test.com", "password": users_factories.DEFAULT_PASSWORD}
    users_factories.UserFactory(email=data["identifier"], password=data["password"])

    # signin with invalid password and ensures the result messsage is generic
    data["password"] = data["password"][:-2]
    response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 400
    assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}


def test_unknown_user_logs_in(client):
    data = {"identifier": "user@test.com", "password": users_factories.DEFAULT_PASSWORD}

    # signin with invalid password and ensures the result messsage is generic
    response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 400
    assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}


def test_user_logs_in_with_missing_fields(client):

    response = client.post("/native/v1/signin", json={})
    assert response.status_code == 400
    assert response.json == {
        "identifier": ["Ce champ est obligatoire"],
        "password": ["Ce champ est obligatoire"],
    }


def test_send_reset_password_email_without_email(client):
    response = client.post("/native/v1/request_password_reset")

    assert response.status_code == 400
    assert response.json["email"] == ["Ce champ est obligatoire"]


def test_request_reset_password_for_unknown_email(client):
    data = {"email": "not_existing_user@example.com"}
    response = client.post("/native/v1/request_password_reset", json=data)

    assert response.status_code == 204


@patch("pcapi.connectors.api_recaptcha.check_native_app_recaptcha_token")
@override_features(ENABLE_NATIVE_APP_RECAPTCHA=True)
def test_request_reset_password_with_recaptcha_ok(
    mock_check_native_app_recaptcha_token,
    client,
):
    email = "existing_user@example.com"
    data = {"email": email}
    user = users_factories.UserFactory(email=email)

    saved_token = Token.query.filter_by(user=user).first()
    assert saved_token is None

    mock_check_native_app_recaptcha_token.return_value = None

    response = client.post("/native/v1/request_password_reset", json=data)

    mock_check_native_app_recaptcha_token.assert_called_once()
    assert response.status_code == 204

    saved_token = Token.query.filter_by(user=user).first()
    assert saved_token.type.value == "reset-password"

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Vars"]["native_app_link"]


def test_request_reset_password_for_existing_email(client):
    email = "existing_user@example.com"
    data = {"email": email}
    user = users_factories.UserFactory(email=email)

    saved_token = Token.query.filter_by(user=user).first()
    assert saved_token is None

    response = client.post("/native/v1/request_password_reset", json=data)

    assert response.status_code == 204

    saved_token = Token.query.filter_by(user=user).first()
    assert saved_token.type.value == "reset-password"
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Vars"]["native_app_link"]


@patch("pcapi.domain.user_emails.send_reset_password_email_to_native_app_user")
def test_request_reset_password_for_inactive_account(mock_send_reset_password_email_to_native_app_user, client):
    email = "existing_user@example.com"
    data = {"email": email}
    users_factories.UserFactory(email=email, isActive=False)

    response = client.post("/native/v1/request_password_reset", json=data)

    assert response.status_code == 204
    mock_send_reset_password_email_to_native_app_user.assert_not_called()


@patch("pcapi.domain.user_emails.send_reset_password_email_to_native_app_user")
def test_request_reset_password_with_mail_service_exception(mock_send_reset_password_email_to_native_app_user, client):
    email = "existing_user@example.com"
    data = {"email": email}
    users_factories.UserFactory(email=email)

    mock_send_reset_password_email_to_native_app_user.return_value = False

    response = client.post("/native/v1/request_password_reset", json=data)

    mock_send_reset_password_email_to_native_app_user.assert_called_once()
    assert response.status_code == 400
    assert response.json["email"] == ["L'email n'a pas pu être envoyé"]


def test_reset_password_with_not_valid_token(client):
    data = {"reset_password_token": "unknwon_token", "new_password": "new_password"}
    user = users_factories.UserFactory()
    old_password = user.password

    response = client.post("/native/v1/reset_password", json=data)

    assert response.status_code == 400
    assert user.password == old_password


def test_reset_password_success(client):
    new_password = "New_password1998!"

    user = users_factories.UserFactory()
    token = users_factories.ResetPasswordToken(user=user)

    data = {"reset_password_token": token.value, "new_password": new_password}
    response = client.post("/native/v1/reset_password", json=data)

    assert response.status_code == 204
    db.session.refresh(user)
    assert user.password == crypto.hash_password(new_password)

    token = Token.query.get(token.id)
    assert token.isUsed


def test_reset_password_for_unvalidated_email(client):
    new_password = "New_password1998!"

    user = users_factories.UserFactory(isEmailValidated=False)
    token = users_factories.ResetPasswordToken(user=user)

    data = {"reset_password_token": token.value, "new_password": new_password}
    response = client.post("/native/v1/reset_password", json=data)

    assert response.status_code == 204
    db.session.refresh(user)
    assert user.password == crypto.hash_password(new_password)
    assert user.isEmailValidated


def test_reset_password_fail_for_password_strength(client):
    user = users_factories.UserFactory()
    token = users_factories.ResetPasswordToken(user=user)

    old_password = user.password
    new_password = "weak_password"

    data = {"reset_password_token": token.value, "new_password": new_password}

    response = client.post("/native/v1/reset_password", json=data)

    assert response.status_code == 400
    db.session.refresh(user)
    assert user.password == old_password
    assert Token.query.get(token.id)


def test_change_password_success(client):
    new_password = "New_password1998!"
    user = users_factories.UserFactory()

    access_token = create_access_token(identity=user.email)
    client.auth_header = {"Authorization": f"Bearer {access_token}"}

    response = client.post(
        "/native/v1/change_password",
        json={"currentPassword": users_factories.DEFAULT_PASSWORD, "newPassword": new_password},
    )

    assert response.status_code == 204
    db.session.refresh(user)
    assert user.password == crypto.hash_password(new_password)


def test_change_password_failures(client):
    new_password = "New_password1998!"
    user = users_factories.UserFactory()

    access_token = create_access_token(identity=user.email)
    client.auth_header = {"Authorization": f"Bearer {access_token}"}

    response = client.post(
        "/native/v1/change_password",
        json={"currentPassword": "wrong_password", "newPassword": new_password},
    )

    assert response.status_code == 400
    assert response.json["code"] == "INVALID_PASSWORD"

    response = client.post(
        "/native/v1/change_password",
        json={"currentPassword": users_factories.DEFAULT_PASSWORD, "newPassword": "weak_password"},
    )

    assert response.status_code == 400
    assert response.json["code"] == "WEAK_PASSWORD"
    db.session.refresh(user)
    assert user.password == crypto.hash_password(users_factories.DEFAULT_PASSWORD)


@patch("pcapi.core.users.repository.get_user_with_valid_token", return_value=None)
def test_validate_email_with_invalid_token(mock_get_user_with_valid_token, client):
    token = "email-validation-token"

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token})

    mock_get_user_with_valid_token.assert_called_once_with(token, [TokenType.EMAIL_VALIDATION], use_token=False)

    assert response.status_code == 400


@freeze_time("2018-06-01")
def test_validate_email_when_eligible(client):
    user = users_factories.UserFactory(
        isEmailValidated=False, dateOfBirth=datetime(2000, 6, 1), departementCode="93", isBeneficiary=False
    )
    token = users_factories.TokenFactory(userId=user.id, type=TokenType.EMAIL_VALIDATION)

    assert not user.isEmailValidated

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token.value})

    assert user.isEmailValidated
    assert response.status_code == 200

    # Ensure the access token is valid
    access_token = response.json["accessToken"]
    client.auth_header = {"Authorization": f"Bearer {access_token}"}
    protected_response = client.get("/native/v1/me")
    assert protected_response.status_code == 200

    # assert we updated the external users
    assert len(bash_testing.requests) == 1
    assert len(sendinblue_testing.sendinblue_requests) == 1

    # Ensure the access token contains user.id
    decoded = decode_token(access_token)
    assert decoded["user_claims"]["user_id"] == user.id

    # Ensure the refresh token is valid
    refresh_token = response.json["refreshToken"]
    client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
    refresh_response = client.post("/native/v1/refresh_access_token", json={})
    assert refresh_response.status_code == 200


@freeze_time("2018-06-01")
def test_validate_email_when_not_eligible(client):
    user = users_factories.UserFactory(isEmailValidated=False, dateOfBirth=datetime(2000, 7, 1))
    token = users_factories.TokenFactory(userId=user.id, type=TokenType.EMAIL_VALIDATION)

    assert not user.isEmailValidated

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token.value})

    assert user.isEmailValidated
    assert response.status_code == 200

    # assert we updated the external users
    assert len(bash_testing.requests) == 1
    assert len(sendinblue_testing.sendinblue_requests) == 1

    # Ensure the access token is valid
    access_token = response.json["accessToken"]
    client.auth_header = {"Authorization": f"Bearer {access_token}"}
    protected_response = client.get("/native/v1/me")
    assert protected_response.status_code == 200

    # Ensure the refresh token is valid
    refresh_token = response.json["refreshToken"]
    client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
    refresh_response = client.post("/native/v1/refresh_access_token", json={})
    assert refresh_response.status_code == 200


@freeze_time("2020-03-15")
def test_refresh_token_route_updates_user_last_connection_date(client):
    data = {"identifier": "user@test.com", "password": users_factories.DEFAULT_PASSWORD}
    user = users_factories.UserFactory(
        email=data["identifier"], password=data["password"], lastConnectionDate=datetime(1990, 1, 1)
    )

    # Get the refresh token
    response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 200
    assert response.json["refreshToken"]
    refresh_token = response.json["refreshToken"]
    bash_testing.reset_requests()
    sendinblue_testing.reset_sendinblue_requests()

    client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
    refresh_response = client.post("/native/v1/refresh_access_token", json={})
    assert refresh_response.status_code == 200

    assert user.lastConnectionDate == datetime(2020, 3, 15)
    assert len(bash_testing.requests) == 1
    assert len(sendinblue_testing.sendinblue_requests) == 1
