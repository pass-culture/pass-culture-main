from datetime import datetime
from datetime import timedelta
import logging
from unittest.mock import patch

from flask_jwt_extended import decode_token
from flask_jwt_extended.utils import create_access_token
from flask_jwt_extended.utils import create_refresh_token
from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.history import factories as history_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription import api as subscription_api
from pcapi.core.testing import override_features
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.models import AccountState
from pcapi.core.users.models import LoginDeviceHistory
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import TrustedDevice
from pcapi.models import db
import pcapi.notifications.push.testing as bash_testing
from pcapi.utils import crypto

from tests.scripts.beneficiary.fixture import make_single_application


pytestmark = pytest.mark.usefixtures("db_session")


def test_account_is_active_account_state(client, caplog):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
    users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

    with caplog.at_level(logging.INFO):
        response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 200
    assert response.json["accountState"] == AccountState.ACTIVE.value
    assert "Successful authentication attempt" in caplog.messages


def test_account_suspended_upon_user_request_account_state(client):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
    user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
    history_factories.SuspendedUserActionHistoryFactory(
        user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
    )

    response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 200
    assert response.json["accountState"] == AccountState.SUSPENDED_UPON_USER_REQUEST.value


def test_account_suspended_by_user_for_suspicious_login_account_state(client):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
    user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
    history_factories.SuspendedUserActionHistoryFactory(
        user=user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
    )

    response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 200
    assert response.json["accountState"] == AccountState.SUSPICIOUS_LOGIN_REPORTED_BY_USER.value


def test_account_deleted_account_state(client):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
    user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
    history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

    response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 400
    assert response.json["code"] == "ACCOUNT_DELETED"


def test_allow_inactive_user_sign(client):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
    users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)

    response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 200


def test_user_logs_in_and_refreshes_token(client):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
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


def test_user_logs_in_with_wrong_password(client, caplog):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
    users_factories.UserFactory(email=data["identifier"], password=data["password"])

    # signin with invalid password and ensures the result messsage is generic
    data["password"] = data["password"][:-2]
    with caplog.at_level(logging.INFO):
        response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 400
    assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
    assert "Failed authentication attempt" in caplog.messages


def test_unknown_user_logs_in(client, caplog):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}

    # signin with invalid password and ensures the result messsage is generic
    with caplog.at_level(logging.INFO):
        response = client.post("/native/v1/signin", json=data)
    assert response.status_code == 400
    assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
    assert "Failed authentication attempt" in caplog.messages


def test_user_logs_in_with_missing_fields(client):
    response = client.post("/native/v1/signin", json={})
    assert response.status_code == 400
    assert response.json == {
        "identifier": ["Ce champ est obligatoire"],
        "password": ["Ce champ est obligatoire"],
    }


class TrustedDeviceFeatureTest:
    data = {
        "identifier": "user@test.com",
        "password": settings.TEST_DEFAULT_PASSWORD,
        "deviceInfo": {
            "deviceId": "2E429592-2446-425F-9A62-D6983F375B3B",
            "source": "iPhone 13",
            "os": "iOS",
        },
    }
    headers = {"X-City": "Paris", "X-Country": "France"}

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True)
    def test_save_login_device_history_on_signin(self, client):
        users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json=self.data, headers=self.headers)

        login_device = LoginDeviceHistory.query.one()

        assert login_device.deviceId == self.data["deviceInfo"]["deviceId"]
        assert login_device.source == "iPhone 13"
        assert login_device.os == "iOS"
        assert login_device.location == "Paris, France"

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True)
    def should_not_save_login_device_history_on_signin_when_no_device_info(self, client):
        users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json={**self.data, "deviceInfo": None})

        assert LoginDeviceHistory.query.count() == 0

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=False)
    def should_not_save_login_device_history_when_feature_flag_is_disabled(self, client):
        users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json=self.data)

        assert LoginDeviceHistory.query.count() == 0

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True)
    def test_save_login_device_as_trusted_device_on_second_signin_with_same_device(self, client):
        user = users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json=self.data)
        client.post("/native/v1/signin", json=self.data)

        trusted_device = TrustedDevice.query.filter(TrustedDevice.deviceId == self.data["deviceInfo"]["deviceId"]).one()
        assert user.trusted_devices == [trusted_device]

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=False)
    def should_not_save_login_device_as_trusted_device_on_second_signin_when_feature_flag_is_inactive(
        self,
        client,
    ):
        user = users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json=self.data)
        client.post("/native/v1/signin", json=self.data)

        assert TrustedDevice.query.count() == 0
        assert user.trusted_devices == []

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True)
    def should_not_save_login_device_as_trusted_device_on_second_signin_when_using_different_devices(self, client):
        first_device = {
            "deviceId": "2E429592-2446-425F-9A62-D6983F375B3B",
            "source": "iPhone 13",
            "os": "iOS",
        }
        second_device = {
            "deviceId": "5F810092-1832-9A32-5B30-P2112F375G3G",
            "source": "Chrome",
            "os": "Mac OS",
        }
        user = users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json={**self.data, "deviceInfo": first_device})
        client.post("/native/v1/signin", json={**self.data, "deviceInfo": second_device})

        assert TrustedDevice.query.count() == 0
        assert user.trusted_devices == []

    @override_features(
        WIP_ENABLE_TRUSTED_DEVICE=True,
        WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=True,
    )
    def should_send_email_when_login_is_suspicious(self, client):
        users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json=self.data, headers=self.headers)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
        assert mails_testing.outbox[0].sent_data["params"]["LOCATION"] == "Paris, France"
        assert mails_testing.outbox[0].sent_data["params"]["OS"] == "iOS"
        assert mails_testing.outbox[0].sent_data["params"]["SOURCE"] == "iPhone 13"
        assert mails_testing.outbox[0].sent_data["params"]["LOGIN_DATE"]
        assert mails_testing.outbox[0].sent_data["params"]["LOGIN_TIME"]
        assert mails_testing.outbox[0].sent_data["params"]["ACCOUNT_SECURING_LINK"]

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True)
    def should_not_send_email_when_logging_in_from_a_trusted_device(self, client):
        user = users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)
        users_factories.TrustedDeviceFactory(user=user)

        client.post("/native/v1/signin", json=self.data)

        assert len(mails_testing.outbox) == 0

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=False)
    def should_not_send_email_when_feature_flag_is_inactive(self, client):
        users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json=self.data)

        assert len(mails_testing.outbox) == 0

    @override_features(
        WIP_ENABLE_TRUSTED_DEVICE=True,
        WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=False,
    )
    def should_not_send_email_when_feature_flag_is_active_but_email_is_inactive(self, client):
        users_factories.UserFactory(email=self.data["identifier"], password=self.data["password"], isActive=True)

        client.post("/native/v1/signin", json=self.data)

        assert len(mails_testing.outbox) == 0


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
    assert mails_testing.outbox[0].sent_data["params"]["RESET_PASSWORD_LINK"]


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
    assert mails_testing.outbox[0].sent_data["params"]["RESET_PASSWORD_LINK"]


class InactiveAccountRequestResetPasswordTest:
    def test_suspended_upon_user_request(self, client):
        user = users_factories.UserFactory(email="existing_user@example.com", isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        response = client.post("/native/v1/request_password_reset", json={"email": user.email})
        self.assert_email_is_sent(response, user)

    def test_suspended_account(self, client):
        user = users_factories.UserFactory(email="existing_user@example.com", isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        response = client.post("/native/v1/request_password_reset", json={"email": user.email})
        self.assert_email_is_sent(response, user)

    def test_deleted_account(self, client):
        user = users_factories.UserFactory(email="existing_user@example.com", isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        response = client.post("/native/v1/request_password_reset", json={"email": user.email})
        self.assert_email_is_sent(response, user)

    def assert_email_is_sent(self, response, user):
        assert response.status_code == 204

        saved_token = Token.query.filter_by(user=user).one()
        assert saved_token.type.value == "reset-password"
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["params"]["RESET_PASSWORD_LINK"]


@patch("pcapi.core.mails.transactional.send_reset_password_email_to_user")
def test_request_reset_password_with_mail_service_exception(mock_send_reset_password_email_to_user, client):
    email = "tt_user@example.com"
    data = {"email": email}
    users_factories.UserFactory(email=email)

    mock_send_reset_password_email_to_user.return_value = False

    response = client.post("/native/v1/request_password_reset", json=data)

    mock_send_reset_password_email_to_user.assert_called_once()
    assert response.status_code == 400
    assert response.json["email"] == ["L'email n'a pas pu être envoyé"]


def test_reset_password_with_not_valid_token(client):
    data = {"reset_password_token": "unknown_token", "new_password": "new_password"}
    user = users_factories.UserFactory()
    old_password = user.password

    response = client.post("/native/v1/reset_password", json=data)

    assert response.status_code == 400
    assert user.password == old_password


def test_reset_password_success(client):
    new_password = "New_password1998!"

    user = users_factories.UserFactory()
    token = users_factories.PasswordResetTokenFactory(user=user)

    data = {"reset_password_token": token.value, "new_password": new_password}
    response = client.post("/native/v1/reset_password", json=data)

    assert response.status_code == 204
    db.session.refresh(user)
    assert user.password == crypto.hash_password(new_password)

    token = Token.query.get(token.id)
    assert token.isUsed


@patch("pcapi.core.subscription.dms.api.try_dms_orphan_adoption")
def test_reset_password_for_unvalidated_email(try_dms_orphan_adoption_mock, client):
    new_password = "New_password1998!"

    user = users_factories.UserFactory(isEmailValidated=False)
    token = users_factories.PasswordResetTokenFactory(user=user)

    data = {"reset_password_token": token.value, "new_password": new_password}
    response = client.post("/native/v1/reset_password", json=data)

    assert response.status_code == 204
    db.session.refresh(user)
    assert user.password == crypto.hash_password(new_password)
    try_dms_orphan_adoption_mock.assert_called_once_with(user)
    assert user.isEmailValidated


def test_reset_password_fail_for_password_strength(client):
    user = users_factories.UserFactory()
    token = users_factories.PasswordResetTokenFactory(user=user)

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
        json={"currentPassword": settings.TEST_DEFAULT_PASSWORD, "newPassword": new_password},
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
        json={"currentPassword": settings.TEST_DEFAULT_PASSWORD, "newPassword": "weak_password"},
    )

    assert response.status_code == 400
    assert response.json["code"] == "WEAK_PASSWORD"
    db.session.refresh(user)
    assert user.password == crypto.hash_password(settings.TEST_DEFAULT_PASSWORD)


@patch("pcapi.core.users.repository.get_user_with_valid_token", side_effect=users_exceptions.InvalidToken)
def test_validate_email_with_invalid_token(mock_get_user_with_valid_token, client):
    token = "email-validation-token"

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token})

    mock_get_user_with_valid_token.assert_called_once_with(token, [TokenType.EMAIL_VALIDATION], use_token=True)

    assert response.status_code == 400


def test_validate_email_with_expired_token(client):
    user = users_factories.UserFactory(isEmailValidated=False)
    token = users_factories.TokenFactory(
        user=user,
        type=TokenType.EMAIL_VALIDATION,
        expirationDate=datetime.utcnow() - timedelta(days=1),
    )

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token.value})

    assert response.status_code == 400

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["template"]["id_prod"] == 201
    assert mails_testing.outbox[0].sent_data["params"]["CONFIRMATION_LINK"]

    assert (
        Token.query.filter(
            Token.userId == user.id, Token.type == TokenType.EMAIL_VALIDATION, Token.expirationDate > datetime.utcnow()
        ).first()
        is not None
    )


@freeze_time("2018-06-01")
def test_validate_email_when_eligible(client):
    user = users_factories.UserFactory(
        isEmailValidated=False,
        dateOfBirth=datetime(2000, 6, 1),
    )
    token = users_factories.TokenFactory(user=user, type=TokenType.EMAIL_VALIDATION)

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token.value})

    assert user.isEmailValidated
    assert response.status_code == 200

    # Ensure the access token is valid
    access_token = response.json["accessToken"]
    client.auth_header = {"Authorization": f"Bearer {access_token}"}
    protected_response = client.get("/native/v1/me")
    assert protected_response.status_code == 200

    # assert we updated the external users
    assert len(bash_testing.requests) == 2
    assert len(sendinblue_testing.sendinblue_requests) == 1

    # Ensure the access token contains user.id
    decoded = decode_token(access_token)
    assert decoded["user_claims"]["user_id"] == user.id

    # Ensure the refresh token is valid
    refresh_token = response.json["refreshToken"]
    client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
    refresh_response = client.post("/native/v1/refresh_access_token", json={})
    assert refresh_response.status_code == 200


def test_validate_email_second_time_is_forbidden(client):
    user = users_factories.UserFactory(isEmailValidated=False)
    token = users_factories.TokenFactory(user=user, type=TokenType.EMAIL_VALIDATION)

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token.value})

    assert user.isEmailValidated
    assert response.status_code == 200

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token.value})
    assert response.status_code == 400
    assert response.json["token"] == ["Le token de validation d'email est invalide."]


@freeze_time("2018-06-01")
def test_validate_email_when_not_eligible(client):
    user = users_factories.UserFactory(isEmailValidated=False, dateOfBirth=datetime(2000, 7, 1))
    token = users_factories.TokenFactory(user=user, type=TokenType.EMAIL_VALIDATION)

    assert not user.isEmailValidated

    response = client.post("/native/v1/validate_email", json={"email_validation_token": token.value})

    assert user.isEmailValidated
    assert response.status_code == 200

    # assert we updated the external users
    assert len(bash_testing.requests) == 2
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


@patch.object(api_dms.DMSGraphQLClient, "execute_query")
def test_validate_email_dms_orphan(execute_query, client):
    application_number = 1234
    email = "dms_orphan@example.com"

    user = users_factories.UserFactory(isEmailValidated=False, dateOfBirth=datetime(2000, 7, 1), email=email)
    token = users_factories.TokenFactory(user=user, type=TokenType.EMAIL_VALIDATION)

    assert not user.isEmailValidated

    fraud_factories.OrphanDmsApplicationFactory(email=email, application_id=application_number)

    execute_query.return_value = make_single_application(
        application_number, dms_models.GraphQLApplicationStates.accepted, email=email
    )
    response = client.post("/native/v1/validate_email", json={"email_validation_token": token.value})

    assert user.isEmailValidated
    assert response.status_code == 200

    fraud_check = subscription_api.get_relevant_identity_fraud_check(user, user.eligibility)
    assert fraud_check is not None


@freeze_time("2020-03-15")
def test_refresh_token_route_updates_user_last_connection_date(client):
    data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
    user = users_factories.UserFactory(
        email=data["identifier"], password=data["password"], lastConnectionDate=datetime(1990, 1, 1)
    )

    refresh_token = create_refresh_token(identity=user.email)

    client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
    refresh_response = client.post("/native/v1/refresh_access_token")
    assert refresh_response.status_code == 200

    assert user.lastConnectionDate == datetime(2020, 3, 15)
    assert len(sendinblue_testing.sendinblue_requests) == 1
