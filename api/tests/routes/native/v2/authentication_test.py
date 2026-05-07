import copy
import logging
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
import time_machine
from flask_jwt_extended import decode_token
from flask_jwt_extended.utils import create_refresh_token

from pcapi import settings
from pcapi.connectors import apple_oauth
from pcapi.core import token as token_utils
from pcapi.core.history import factories as history_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import schemas as users_schemas
from pcapi.core.users import testing as brevo_testing
from pcapi.core.users.models import AccountState
from pcapi.core.users.models import NativeUserSession
from pcapi.core.users.models import SingleSignOn
from pcapi.models import db


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
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        with caplog.at_level(logging.INFO):
            response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.ACTIVE.value
        assert "Successful authentication attempt" in caplog.messages
        assert (
            db.session.query(NativeUserSession)
            .filter(
                NativeUserSession.accessToken == decode_token(response.json["accessToken"])["jti"],
                NativeUserSession.refreshToken == decode_token(response.json["refreshToken"])["jti"],
                NativeUserSession.deviceId == self.device_info["deviceId"],
                NativeUserSession.userId == user.id,
            )
            .count()
        )

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

        refresh_token = create_refresh_token(identity=str(user.id))
        users_factories.NativeUserSessionFactory(
            user=user,
            refreshToken=decode_token(refresh_token)["jti"],
            deviceId=self.device_info["deviceId"],
        )

        client.with_explicit_token(refresh_token)
        refresh_response = client.post("/native/v2/refresh_access_token", json={"device_info": self.device_info})
        assert refresh_response.status_code == 200

        assert refresh_response.json["refreshToken"] != refresh_token
        assert user.lastConnectionDate == datetime(2020, 3, 15)
        assert len(brevo_testing.brevo_requests) == 1

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
        assert db.session.query(NativeUserSession).count() == 1
        assert (
            db.session.query(NativeUserSession)
            .filter(
                NativeUserSession.accessToken == decode_token(response.json["accessToken"])["jti"],
                NativeUserSession.refreshToken == decode_token(response.json["refreshToken"])["jti"],
                NativeUserSession.deviceId == self.device_info["deviceId"],
                NativeUserSession.userId == user.id,
            )
            .count()
        )

        refresh_token = response.json["refreshToken"]
        access_token = response.json["accessToken"]

        # Ensure the access token is valid
        client.with_explicit_token(access_token)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        # Ensure the access token contains user.id
        decoded = decode_token(access_token)
        assert decoded["sub"] == str(user.id)

        # Ensure the refresh token can generate a new access token
        client.with_explicit_token(refresh_token)
        response = client.post("/native/v2/refresh_access_token", json={"device_info": self.device_info})
        assert response.status_code == 200, response.json
        assert db.session.query(NativeUserSession).count() == 1
        assert (
            db.session.query(NativeUserSession)
            .filter(
                NativeUserSession.accessToken == decode_token(response.json["accessToken"])["jti"],
                NativeUserSession.refreshToken == decode_token(response.json["refreshToken"])["jti"],
                NativeUserSession.deviceId == self.device_info["deviceId"],
                NativeUserSession.userId == user.id,
            )
            .count()
        )
        access_token = response.json["accessToken"]

        # Ensure the new access token is valid
        client.with_explicit_token(access_token)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        # Ensure the new access token contains user.id
        decoded = decode_token(access_token)
        assert decoded["sub"] == str(user.id)

    def test_device_info_required(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"])

        # Get the refresh
        response = client.post("/native/v2/signin", json=data)
        assert response.status_code == 200
        assert db.session.query(NativeUserSession).count() == 1
        assert (
            db.session.query(NativeUserSession)
            .filter(
                NativeUserSession.accessToken == decode_token(response.json["accessToken"])["jti"],
                NativeUserSession.refreshToken == decode_token(response.json["refreshToken"])["jti"],
                NativeUserSession.deviceId == self.device_info["deviceId"],
                NativeUserSession.userId == user.id,
            )
            .count()
        )

        refresh_token = response.json["refreshToken"]

        # Ensure the device_info is needed for access token refresh
        client.with_explicit_token(refresh_token)
        response = client.post("/native/v2/refresh_access_token", json={})
        assert response.status_code == 400, response.json

        # Ensure the device_id is mandatory for access token refresh
        response = client.post("/native/v2/refresh_access_token", json={"device_info": {"os": "iOS", "source": "app"}})
        assert response.status_code == 400, response.json

    def test_invalid_device_id(self, client):
        user = users_factories.UserFactory()

        refresh_token = create_refresh_token(identity=str(user.id))
        old_session = users_factories.NativeUserSessionFactory(
            user=user,
            refreshToken=decode_token(refresh_token)["jti"],
            deviceId="something different",
        )

        client.with_explicit_token(refresh_token)
        refresh_response = client.post("/native/v2/refresh_access_token", json={"device_info": self.device_info})
        assert refresh_response.status_code == 401

        assert db.session.query(users_models.NativeUserSession).count() == 1
        assert (
            db.session.query(users_models.NativeUserSession)
            .filter(users_models.NativeUserSession.id == old_session.id)
            .count()
            == 1
        )

    def test_no_device_id(self, client):
        user = users_factories.UserFactory()

        refresh_token = create_refresh_token(identity=str(user.id))
        users_factories.NativeUserSessionFactory(
            user=user,
            refreshToken=decode_token(refresh_token)["jti"],
            deviceId="",
        )

        client.with_explicit_token(refresh_token)
        refresh_response = client.post("/native/v2/refresh_access_token", json={"device_info": self.device_info})
        assert refresh_response.status_code == 200

        assert db.session.query(users_models.NativeUserSession).count() == 1
        assert refresh_response.json["refreshToken"] != refresh_token

    def test_no_session(self, client):
        user = users_factories.UserFactory()
        refresh_token = create_refresh_token(identity=str(user.id))

        client.with_explicit_token(refresh_token)
        refresh_response = client.post("/native/v2/refresh_access_token", json={"device_info": self.device_info})
        assert refresh_response.status_code == 401

        assert db.session.query(users_models.NativeUserSession).count() == 0

    def test_with_legacy_token(self, client):
        user = users_factories.UserFactory(email="user@test.com")
        refresh_token = create_refresh_token(identity=user.email, additional_claims={"user_id": user.id})

        client.with_explicit_token(refresh_token)
        response = client.post("/native/v2/refresh_access_token", json={"device_info": self.device_info})
        assert response.status_code == 200
        assert db.session.query(NativeUserSession).count() == 1
        assert (
            db.session.query(NativeUserSession)
            .filter(
                NativeUserSession.accessToken == decode_token(response.json["accessToken"])["jti"],
                NativeUserSession.refreshToken == decode_token(response.json["refreshToken"])["jti"],
                NativeUserSession.deviceId == self.device_info["deviceId"],
                NativeUserSession.userId == user.id,
            )
            .count()
        )


class SSOSigninTest:
    valid_sso_user = users_schemas.SSOUser(
        sub="100428144463745704968",
        email="docteur.cuesta@passkoultour.app",
        email_verified=True,
    )
    device_info = {
        "os": "iOS",
        "deviceId": "ID",
        "source": "app",
    }

    def test_fails_if_unknown_provider(self, client):
        response = client.post(
            "/native/v2/oauth/unknown_sso/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": "wontbechecked",
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 400

    @patch("pcapi.connectors.apple_oauth.get_apple_user")
    def test_cant_fetch_apple_user(self, mocked_apple_oauth, client):
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_apple_oauth.side_effect = apple_oauth.AppleSignInException

        response = client.post(
            "/native/v2/oauth/apple/authorize",
            json={
                "authorizationCode": "4/apple_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 401
        assert response.json["code"] == "SSO_ERROR"
        assert response.json["general"] == "L'authentification a échoué"

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_account_is_active(self, mocked_google_oauth, client, caplog):
        users_factories.SingleSignOnFactory(
            ssoUserId=self.valid_sso_user.sub, user__email=self.valid_sso_user.email, user__isActive=True
        )
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        with caplog.at_level(logging.INFO):
            response = client.post(
                "/native/v2/oauth/google/authorize",
                json={
                    "authorizationCode": "4/google_code",
                    "oauthStateToken": oauth_state_token.encoded_token,
                    "device_info": self.device_info,
                },
            )

        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.ACTIVE.value
        assert "Successful authentication attempt" in caplog.messages

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_account_is_deleted(self, mocked_google_oauth, client):
        user = users_factories.UserFactory(email=self.valid_sso_user.email, isActive=False)
        users_factories.SingleSignOnFactory(user=user, ssoUserId=self.valid_sso_user.sub)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 400
        assert response.json["code"] == "SSO_ERROR"

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_account_is_anonymized(self, mocked_google_oauth, client):
        user = users_factories.AnonymizedUserFactory(email=self.valid_sso_user.email)
        users_factories.SingleSignOnFactory(user=user, ssoUserId=self.valid_sso_user.sub)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 400
        assert response.json["code"] == "SSO_ERROR"

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_account_creation_token_if_account_does_not_exist(self, mocked_google_oauth, client, caplog):
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        with caplog.at_level(logging.INFO):
            response = client.post(
                "/native/v2/oauth/google/authorize",
                json={
                    "authorizationCode": "4/google_code",
                    "oauthStateToken": oauth_state_token.encoded_token,
                    "device_info": self.device_info,
                },
            )

        assert response.status_code == 401
        assert set(["code", "accountCreationToken", "general", "email"]) == response.json.keys()
        assert response.json["code"] == "SSO_EMAIL_NOT_FOUND"
        assert response.json["email"] == self.valid_sso_user.email

        decoded_account_creation_token = token_utils.UUIDToken.load_without_checking(
            response.json["accountCreationToken"]
        )
        assert uuid.UUID(decoded_account_creation_token.key_suffix)
        assert users_schemas.SSOUser.model_validate(decoded_account_creation_token.data)
        assert not decoded_account_creation_token.check(
            token_utils.TokenType.ACCOUNT_CREATION, decoded_account_creation_token.key_suffix
        )

    @pytest.mark.parametrize("sso_provider", ("apple", "google"))
    @patch("pcapi.connectors.google_oauth.get_google_user")
    @patch("pcapi.connectors.apple_oauth.get_apple_user")
    def test_updates_single_sign_on_email_change(self, mocked_apple_oauth, mocked_google_oauth, sso_provider, client):
        user = users_factories.UserFactory(isActive=True)
        google_sso = users_factories.SingleSignOnFactory(user=user, ssoUserId="old id", ssoProvider=sso_provider)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_apple_oauth.return_value = self.valid_sso_user
        mocked_google_oauth.return_value = self.valid_sso_user
        user.email = self.valid_sso_user.email

        response = client.post(
            f"/native/v2/oauth/{sso_provider}/authorize",
            json={
                "authorizationCode": "fakeAuthCode",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 200
        assert google_sso.ssoUserId == self.valid_sso_user.sub

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_single_sign_on_inserts_sso_method_if_email_found(self, mocked_google_oauth, client):
        user = users_factories.UserFactory(email=self.valid_sso_user.email, isActive=True)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 200

        created_sso = (
            db.session.query(SingleSignOn).filter(SingleSignOn.user == user, SingleSignOn.ssoProvider == "google").one()
        )
        assert created_sso.ssoUserId == self.valid_sso_user.sub

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_single_sign_on_raises_if_email_not_validated(self, mocked_google_oauth, client):
        users_factories.UserFactory(email=self.valid_sso_user.email, isActive=True)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        unvalidated_email_google_user = copy.deepcopy(self.valid_sso_user)
        unvalidated_email_google_user.email_verified = False
        mocked_google_oauth.return_value = unvalidated_email_google_user

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 400

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_single_sign_on_validates_email_and_deletes_password(self, mocked_google_oauth, client, caplog):
        user = users_factories.UserFactory(email=self.valid_sso_user.email, isEmailValidated=False)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 200, response.json
        assert user.isEmailValidated
        assert user.password is None

    @pytest.mark.parametrize("sso_provider", ("apple", "google"))
    @patch("pcapi.connectors.google_oauth.get_google_user")
    @patch("pcapi.connectors.apple_oauth.get_apple_user")
    def test_single_sign_on_does_not_duplicate_ssos(
        self, mocked_apple_oauth, mocked_google_oauth, sso_provider, client
    ):
        single_sign_on = users_factories.SingleSignOnFactory(
            user__email=self.valid_sso_user.email, ssoUserId=self.valid_sso_user.sub, ssoProvider=sso_provider
        )
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_apple_oauth.return_value = self.valid_sso_user
        mocked_google_oauth.return_value = self.valid_sso_user

        response = client.post(
            f"/native/v2/oauth/{sso_provider}/authorize",
            json={
                "authorizationCode": "fakeAuthCode",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 200
        assert db.session.query(SingleSignOn).filter(SingleSignOn.user == single_sign_on.user).count() == 1

    def test_oauth_state_token_past_expiration_date(self, client):
        with time_machine.travel("2022-01-01"):
            oauth_state_token = token_utils.UUIDToken.create(
                token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
            )

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 400, response.json
        assert response.json["code"] == "SSO_LOGIN_TIMEOUT"

    def test_oauth_state_token_expired(self, client):
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        oauth_state_token.expire()

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 400, response.json
        assert response.json["code"] == "SSO_LOGIN_TIMEOUT"

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_authorization_expires_oauth_state_token(self, mocked_google_oauth, client):
        users_factories.SingleSignOnFactory(
            ssoUserId=self.valid_sso_user.sub, user__email=self.valid_sso_user.email, user__isActive=True
        )
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 200, response.json
        assert not token_utils.UUIDToken.token_exists(token_utils.TokenType.OAUTH_STATE, oauth_state_token.key_suffix)

    def test_oauth_state_token_creation(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v2/oauth/state")
            assert response.status_code == 200, response.json

        oauth_state_token = token_utils.UUIDToken.load_without_checking(response.json["oauthStateToken"])
        assert uuid.UUID(oauth_state_token.key_suffix)
        assert not oauth_state_token.check(token_utils.TokenType.OAUTH_STATE, oauth_state_token.key_suffix)

    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_oauth_state_token_roundtrip(self, mocked_google_oauth, client):
        users_factories.SingleSignOnFactory(
            ssoUserId=self.valid_sso_user.sub, user__email=self.valid_sso_user.email, user__isActive=True
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        oauth_state_token_response = client.get("/native/v2/oauth/state")
        authorization_response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token_response.json["oauthStateToken"],
                "device_info": self.device_info,
            },
        )

        assert authorization_response.status_code == 200, authorization_response.json

    @pytest.mark.parametrize("header,is_web", [("web", True), ("", False), ("other", False)])
    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_get_platform_from_request_headers(self, mocked_google_oauth, client, header, is_web):
        users_factories.SingleSignOnFactory(
            ssoUserId=self.valid_sso_user.sub, user__email=self.valid_sso_user.email, user__isActive=True
        )
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_sso_user

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token.encoded_token,
                "device_info": self.device_info,
            },
            headers={"platform": header},
        )

        assert response.status_code == 200, response.json
        mocked_google_oauth.assert_called_with("4/google_code", is_web)

    def test_single_sign_on_fail_when_missing_device_info(self, client):
        users_factories.SingleSignOnFactory(
            ssoUserId=self.valid_sso_user.sub, user__email=self.valid_sso_user.email, user__isActive=True
        )
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )

        response = client.post(
            "/native/v2/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 400
