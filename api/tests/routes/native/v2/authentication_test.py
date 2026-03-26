import logging
from datetime import datetime
from unittest.mock import patch

import pytest
import time_machine
from flask_jwt_extended import decode_token
from flask_jwt_extended.utils import create_refresh_token

from pcapi import settings
from pcapi.core.history import factories as history_factories
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.models import AccountState


pytestmark = pytest.mark.usefixtures("db_session")


class SigninTest:
    device_info = {
        "os": "iOS",
        "deviceId": "ID",
        "source": "app",
    }

    def test_account_is_active_account_state(self, client, caplog):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        with caplog.at_level(logging.INFO):
            response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.ACTIVE.value
        assert "Successful authentication attempt" in caplog.messages

    def test_account_suspended_upon_user_request_account_state(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.SUSPENDED_UPON_USER_REQUEST.value

    def test_account_anonymized_user_request_account_state(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.AnonymizedUserFactory(
            email=data["identifier"],
            password=data["password"],
        )
        response = client.post("/native/v2/signin", json=data)

        assert response.status_code == 400
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}

    def test_account_suspended_by_user_for_suspicious_login_account_state(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        )

        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.SUSPICIOUS_LOGIN_REPORTED_BY_USER.value

    def test_account_suspended_by_user_for_anonymization(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.WAITING_FOR_ANONYMIZATION
        )

        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.WAITING_FOR_ANONYMIZATION.value

    def test_account_deleted_account_state(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 400
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}

    def test_allow_inactive_user_sign(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)

        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 200

    def test_user_logs_in_with_wrong_password(self, client, caplog):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        # signin with invalid password and ensures the result messsage is generic
        data["password"] = data["password"][:-2]
        with caplog.at_level(logging.INFO):
            response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 400
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert "Failed authentication attempt" in caplog.messages

    def test_unknown_user_logs_in(self, client, caplog):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }

        # signin with invalid password and ensures the result messsage is generic
        with caplog.at_level(logging.INFO):
            response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 400
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert "Failed authentication attempt" in caplog.messages

    def test_user_without_password_logs_in(self, client, caplog):
        user = users_factories.UserFactory(password=None, isActive=True)

        response = client.post(
            "/native/v2/signin",
            json={
                "identifier": user.email,
                "password": settings.TEST_DEFAULT_PASSWORD,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 400
        # generic message to prevent enumeration attack
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}

    def test_user_logs_in_with_missing_fields(self, client):
        response = client.post("/native/v2/signin", json={})
        assert response.status_code == 400
        assert response.json == {
            "identifier": ["Ce champ est obligatoire"],
            "password": ["Ce champ est obligatoire"],
            "deviceInfo": ["Ce champ est obligatoire"],
        }

    @pytest.mark.settings(RECAPTCHA_IGNORE_VALIDATION=0)
    @pytest.mark.features(ENABLE_NATIVE_APP_RECAPTCHA=False)
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def should_not_check_recaptcha_when_feature_flag_is_disabled(self, mocked_recaptcha_validation, client):
        mocked_recaptcha_validation.return_value = {"success": False, "error-codes": []}
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "invalid_token",
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post("/native/v2/signin", json=data)

        assert response.status_code == 200

    @pytest.mark.settings(RECAPTCHA_IGNORE_VALIDATION=0)
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    @pytest.mark.parametrize("error", ["invalid-input-response", "timeout-or-duplicate"])
    def test_fail_when_recaptcha_token_is_invalid(self, mocked_recaptcha_validation, error, client):
        mocked_recaptcha_validation.return_value = {"success": False, "error-codes": [error]}
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "invalid_token",
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post("/native/v2/signin", json=data)

        assert response.status_code == 401
        assert response.json == {"token": "Le token est invalide"}

    @pytest.mark.settings(RECAPTCHA_IGNORE_VALIDATION=0)
    def test_fail_when_recaptcha_token_is_missing(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post("/native/v2/signin", json=data)

        assert response.status_code == 401
        assert response.json == {"token": "Le token est invalide"}

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_success_when_recaptcha_token_is_valid(self, mocked_check_recaptcha_token_is_valid, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "valid_token",
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post("/native/v2/signin", json=data)

        mocked_check_recaptcha_token_is_valid.assert_called()
        assert response.status_code == 200

    def test_fail_when_missing_device_info(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 400

        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "deviceInfo": {
                "os": "Windows XP",
                "source": "app",
            },
        }
        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 400

    def test_fail_when_extra_device_info(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "deviceInfo": {
                "os": "Windows XP",
                "deviceId": "ID",
                "source": "app",
                "fontScale": -1,
                "resolution": "750x1334",
                "screenZoomLevel": None,
            },
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 400


class RefreshAccessTokenTest:
    device_info = {
        "os": "iOS",
        "deviceId": "ID",
        "source": "app",
    }

    @time_machine.travel("2020-03-15", tick=False)
    def test_refresh_token_route_updates_user_last_connection_date(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(
            email=data["identifier"], password=data["password"], lastConnectionDate=datetime(1990, 1, 1)
        )

        refresh_token = create_refresh_token(identity=user.email)

        client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
        refresh_response = client.post("/native/v1/refresh_access_token")
        assert refresh_response.status_code == 200

        assert user.lastConnectionDate == datetime(2020, 3, 15)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    def test_user_logs_in_and_refreshes_token(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"])

        # Get the refresh and access token
        response = client.post("/native/v2/signin", json=data)
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
