import copy
from datetime import datetime
import logging
from unittest.mock import patch
import uuid

from flask_jwt_extended import decode_token
from flask_jwt_extended.utils import create_access_token
from flask_jwt_extended.utils import create_refresh_token
import pytest
import time_machine

from pcapi import settings
from pcapi.connectors import google_oauth
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.connectors.google_oauth import GoogleUser
from pcapi.core import token as token_utils
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.history import factories as history_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription import api as subscription_api
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.models import AccountState
from pcapi.core.users.models import LoginDeviceHistory
from pcapi.core.users.models import SingleSignOn
from pcapi.core.users.models import TrustedDevice
from pcapi.models import db
import pcapi.notifications.push.testing as bash_testing
from pcapi.utils import crypto

from tests.scripts.beneficiary.fixture import make_single_application


pytestmark = pytest.mark.usefixtures("db_session")


class SigninTest:
    def test_account_is_active_account_state(self, client, caplog):
        data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        with caplog.at_level(logging.INFO):
            response = client.post("/native/v1/signin", json=data)
        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.ACTIVE.value
        assert "Successful authentication attempt" in caplog.messages

    def test_account_suspended_upon_user_request_account_state(self, client):
        data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        response = client.post("/native/v1/signin", json=data)
        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.SUSPENDED_UPON_USER_REQUEST.value

    def test_account_anonymized_user_request_account_state(self, client):
        data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        users_factories.AnonymizedUserFactory(
            email=data["identifier"],
            password=data["password"],
        )
        response = client.post("/native/v1/signin", json=data)

        assert response.status_code == 400
        assert response.json["code"] == "ACCOUNT_ANONYMIZED"

    def test_account_suspended_by_user_for_suspicious_login_account_state(self, client):
        data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        )

        response = client.post("/native/v1/signin", json=data)
        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.SUSPICIOUS_LOGIN_REPORTED_BY_USER.value

    def test_account_deleted_account_state(self, client):
        data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        response = client.post("/native/v1/signin", json=data)
        assert response.status_code == 400
        assert response.json["code"] == "ACCOUNT_DELETED"

    def test_allow_inactive_user_sign(self, client):
        data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)

        response = client.post("/native/v1/signin", json=data)
        assert response.status_code == 200

    def test_user_logs_in_and_refreshes_token(self, client):
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

    def test_user_logs_in_with_wrong_password(self, client, caplog):
        data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        # signin with invalid password and ensures the result messsage is generic
        data["password"] = data["password"][:-2]
        with caplog.at_level(logging.INFO):
            response = client.post("/native/v1/signin", json=data)
        assert response.status_code == 400
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert "Failed authentication attempt" in caplog.messages

    def test_unknown_user_logs_in(self, client, caplog):
        data = {"identifier": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}

        # signin with invalid password and ensures the result messsage is generic
        with caplog.at_level(logging.INFO):
            response = client.post("/native/v1/signin", json=data)
        assert response.status_code == 400
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert "Failed authentication attempt" in caplog.messages

    def test_user_logs_in_with_missing_fields(self, client):
        response = client.post("/native/v1/signin", json={})
        assert response.status_code == 400
        assert response.json == {
            "identifier": ["Ce champ est obligatoire"],
            "password": ["Ce champ est obligatoire"],
        }

    @override_features(ENABLE_NATIVE_APP_RECAPTCHA=False)
    @override_settings(RECAPTCHA_IGNORE_VALIDATION=0)
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def should_not_check_recaptcha_when_feature_flag_is_disabled(self, mocked_recaptcha_validation, client):
        mocked_recaptcha_validation.return_value = {"success": False, "error-codes": []}
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "invalid_token",
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post("/native/v1/signin", json=data)

        assert response.status_code == 200

    @override_settings(RECAPTCHA_IGNORE_VALIDATION=0)
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    @pytest.mark.parametrize("error", ["invalid-input-response", "timeout-or-duplicate"])
    def test_fail_when_recaptcha_token_is_invalid(self, mocked_recaptcha_validation, error, client):
        mocked_recaptcha_validation.return_value = {"success": False, "error-codes": [error]}
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "invalid_token",
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post("/native/v1/signin", json=data)

        assert response.status_code == 401
        assert response.json == {"token": "Le token est invalide"}

    @override_settings(RECAPTCHA_IGNORE_VALIDATION=0)
    def test_fail_when_recaptcha_token_is_missing(self, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post("/native/v1/signin", json=data)

        assert response.status_code == 401
        assert response.json == {"token": "Le token est invalide"}

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_success_when_recaptcha_token_is_valid(self, mocked_check_recaptcha_token_is_valid, client):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "valid_token",
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post("/native/v1/signin", json=data)

        mocked_check_recaptcha_token_is_valid.assert_called()
        assert response.status_code == 200

    @time_machine.travel("2020-03-15", tick=False)
    def test_refresh_token_route_updates_user_last_connection_date(self, client):
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


class SSOSigninTest:
    valid_google_user = GoogleUser(
        sub="100428144463745704968",
        email="docteur.cuesta@passculture.app",
        email_verified=True,
    )

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_account_is_active(self, mocked_google_oauth, client, caplog):
        users_factories.SingleSignOnFactory(
            ssoUserId=self.valid_google_user.sub, user__email=self.valid_google_user.email, user__isActive=True
        )
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        with caplog.at_level(logging.INFO):
            response = client.post(
                "/native/v1/oauth/google/authorize",
                json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
            )

        assert response.status_code == 200
        assert response.json["accountState"] == AccountState.ACTIVE.value
        assert "Successful authentication attempt" in caplog.messages

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_account_is_deleted(self, mocked_google_oauth, client):
        user = users_factories.UserFactory(email=self.valid_google_user.email, isActive=False)
        users_factories.SingleSignOnFactory(user=user, ssoUserId=self.valid_google_user.sub)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 400
        assert response.json["code"] == "SSO_ACCOUNT_DELETED"

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_account_is_anonymized(self, mocked_google_oauth, client):
        user = users_factories.AnonymizedUserFactory(email=self.valid_google_user.email)
        users_factories.SingleSignOnFactory(user=user, ssoUserId=self.valid_google_user.sub)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 400
        assert response.json["code"] == "SSO_ACCOUNT_ANONYMIZED"

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_account_creation_token_if_account_does_not_exist(self, mocked_google_oauth, client, caplog):
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        with caplog.at_level(logging.INFO):
            response = client.post(
                "/native/v1/oauth/google/authorize",
                json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
            )

        assert response.status_code == 401
        assert set(["code", "accountCreationToken", "general", "email"]) == response.json.keys()
        assert response.json["code"] == "SSO_EMAIL_NOT_FOUND"
        assert response.json["email"] == self.valid_google_user.email

        decoded_account_creation_token = token_utils.UUIDToken.load_without_checking(
            response.json["accountCreationToken"]
        )
        assert uuid.UUID(decoded_account_creation_token.key_suffix)
        assert google_oauth.GoogleUser.model_validate(decoded_account_creation_token.data)
        assert not decoded_account_creation_token.check(
            token_utils.TokenType.ACCOUNT_CREATION, decoded_account_creation_token.key_suffix
        )

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_single_sign_on_ignores_email_if_found(self, mocked_google_oauth, client):
        user = users_factories.UserFactory(email="another@email.com", isActive=True)
        users_factories.SingleSignOnFactory(user=user, ssoUserId=self.valid_google_user.sub)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 200

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_single_sign_on_inserts_sso_method_if_email_found(self, mocked_google_oauth, client):
        user = users_factories.UserFactory(email=self.valid_google_user.email, isActive=True)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 200

        created_sso = SingleSignOn.query.filter(SingleSignOn.user == user, SingleSignOn.ssoProvider == "google").one()
        assert created_sso.ssoUserId == self.valid_google_user.sub

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_single_sign_on_raises_if_email_not_validated(self, mocked_google_oauth, client):
        users_factories.UserFactory(email=self.valid_google_user.email, isActive=True)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        unvalidated_email_google_user = copy.deepcopy(self.valid_google_user)
        unvalidated_email_google_user.email_verified = False
        mocked_google_oauth.return_value = unvalidated_email_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 400

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_single_sign_on_validates_email_and_deletes_password(self, mocked_google_oauth, client, caplog):
        user = users_factories.UserFactory(email=self.valid_google_user.email, isEmailValidated=False)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 200, response.json
        assert user.isEmailValidated
        assert user.password is None

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_single_sign_on_does_not_duplicate_ssos(self, mocked_google_oauth, client):
        single_sign_on = users_factories.SingleSignOnFactory(ssoUserId=self.valid_google_user.sub)
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 200
        assert SingleSignOn.query.filter(SingleSignOn.user == single_sign_on.user).count() == 1

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_single_sign_on_raises_if_another_sso_is_already_configured(self, mocked_google_oauth, client):
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        users_factories.SingleSignOnFactory(user__email=self.valid_google_user.email)
        mocked_google_oauth.return_value = self.valid_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 400
        assert SingleSignOn.query.filter(SingleSignOn.ssoUserId == self.valid_google_user.sub).count() == 0

    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_oauth_state_token_past_expiration_date(self, client):
        with time_machine.travel("2022-01-01"):
            oauth_state_token = token_utils.UUIDToken.create(
                token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
            )

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 400, response.json
        assert response.json["code"] == "SSO_LOGIN_TIMEOUT"

    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_oauth_state_token_expired(self, client):
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        oauth_state_token.expire()

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 400, response.json
        assert response.json["code"] == "SSO_LOGIN_TIMEOUT"

    @patch("pcapi.connectors.google_oauth.get_google_user")
    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_authorization_expires_oauth_state_token(self, mocked_google_oauth, client):
        users_factories.SingleSignOnFactory(
            ssoUserId=self.valid_google_user.sub, user__email=self.valid_google_user.email, user__isActive=True
        )
        oauth_state_token = token_utils.UUIDToken.create(
            token_utils.TokenType.OAUTH_STATE, users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME
        )
        mocked_google_oauth.return_value = self.valid_google_user

        response = client.post(
            "/native/v1/oauth/google/authorize",
            json={"authorizationCode": "4/google_code", "oauthStateToken": oauth_state_token.encoded_token},
        )

        assert response.status_code == 200, response.json
        assert not token_utils.UUIDToken.token_exists(token_utils.TokenType.OAUTH_STATE, oauth_state_token.key_suffix)

    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    def test_oauth_state_token_creation(self, client):
        response = client.get("/native/v1/oauth/state")

        assert response.status_code == 200, response.json

        oauth_state_token = token_utils.UUIDToken.load_without_checking(response.json["oauthStateToken"])
        assert uuid.UUID(oauth_state_token.key_suffix)
        assert not oauth_state_token.check(token_utils.TokenType.OAUTH_STATE, oauth_state_token.key_suffix)

    @override_features(WIP_ENABLE_GOOGLE_SSO=True)
    @patch("pcapi.connectors.google_oauth.get_google_user")
    def test_oauth_state_token_roundtrip(self, mocked_google_oauth, client):
        users_factories.SingleSignOnFactory(
            ssoUserId=self.valid_google_user.sub, user__email=self.valid_google_user.email, user__isActive=True
        )
        mocked_google_oauth.return_value = self.valid_google_user

        oauth_state_token_response = client.get("/native/v1/oauth/state")
        authorization_response = client.post(
            "/native/v1/oauth/google/authorize",
            json={
                "authorizationCode": "4/google_code",
                "oauthStateToken": oauth_state_token_response.json["oauthStateToken"],
            },
        )

        assert authorization_response.status_code == 200, authorization_response.json

    def test_sso_is_feature_flagged(self, client):
        response = client.post("/native/v1/oauth/google/authorize", json={"code": "4/google_code"})

        assert response.status_code == 400


class TrustedDeviceFeatureTest:
    @pytest.mark.parametrize(
        "signin_route,data",
        [
            (
                "signin",
                {
                    "identifier": "user@test.com",
                    "password": settings.TEST_DEFAULT_PASSWORD,
                    "deviceInfo": {
                        "deviceId": "2E429592-2446-425F-9A62-D6983F375B3B",
                        "source": "iPhone 13",
                        "os": "iOS",
                    },
                },
            ),
            (
                "oauth/google/authorize",
                {
                    "authorizationCode": "4/google_code",
                    "oauth_state_token": "eyJhbG.real.jwt.token",
                    "deviceInfo": {
                        "deviceId": "2E429592-2446-425F-9A62-D6983F375B3B",
                        "source": "iPhone 13",
                        "os": "iOS",
                    },
                },
            ),
        ],
    )
    class TrustedDeviceSigninTest:
        headers = {"X-City": "Paris", "X-Country": "France"}
        one_month_in_seconds = 31 * 24 * 60 * 60
        one_year_in_seconds = 366 * 24 * 60 * 60
        valid_google_user = GoogleUser(
            sub="100428144463745704968",
            email="user@test.com",
            email_verified=True,
        )

        def setup_method(self):
            self.valid_oauth_state_token = token_utils.UUIDToken.create(token_utils.TokenType.OAUTH_STATE, ttl=None)

        def teardown_method(self):
            self.valid_oauth_state_token.expire()

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def test_save_login_device_history_on_signin(
            self,
            mocked_google_oauth,
            mocked_load_and_check_oauth_token,
            client,
            signin_route,
            data,
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True)

            client.post(f"/native/v1/{signin_route}", json=data, headers=self.headers)

            login_device = LoginDeviceHistory.query.one()

            assert login_device.deviceId == data["deviceInfo"]["deviceId"]
            assert login_device.source == "iPhone 13"
            assert login_device.os == "iOS"
            assert login_device.location == "Paris, France"

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_not_save_login_device_history_on_signin_when_no_device_info(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True)

            client.post(f"/native/v1/{signin_route}", json={**data, "deviceInfo": None})

            assert LoginDeviceHistory.query.count() == 0

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=False)
        def should_not_save_login_device_history_when_feature_flag_is_disabled(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True)

            client.post(f"/native/v1/{signin_route}", json=data)

            assert LoginDeviceHistory.query.count() == 0

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def test_save_login_device_as_trusted_device_on_second_signin_with_same_device(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            user = users_factories.UserFactory(
                email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True
            )

            client.post(f"/native/v1/{signin_route}", json=data)
            client.post(f"/native/v1/{signin_route}", json=data)

            trusted_device = TrustedDevice.query.filter(TrustedDevice.deviceId == data["deviceInfo"]["deviceId"]).one()
            assert user.trusted_devices == [trusted_device]

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=False)
        def should_not_save_login_device_as_trusted_device_on_second_signin_when_feature_flag_is_inactive(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            user = users_factories.UserFactory(
                email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True
            )

            client.post(f"/native/v1/{signin_route}", json=data)
            client.post(f"/native/v1/{signin_route}", json=data)

            assert TrustedDevice.query.count() == 0
            assert user.trusted_devices == []

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_not_save_login_device_as_trusted_device_on_second_signin_when_using_different_devices(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
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
            user = users_factories.UserFactory(
                email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True
            )

            client.post(f"/native/v1/{signin_route}", json={**data, "deviceInfo": first_device})
            client.post(f"/native/v1/{signin_route}", json={**data, "deviceInfo": second_device})

            assert TrustedDevice.query.count() == 0
            assert user.trusted_devices == []

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_send_email_when_login_is_suspicious(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True)

            client.post(f"/native/v1/{signin_route}", json=data, headers=self.headers)

            assert len(mails_testing.outbox) == 1
            assert mails_testing.outbox[0]["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
            assert mails_testing.outbox[0]["params"]["LOCATION"] == "Paris, France"
            assert mails_testing.outbox[0]["params"]["OS"] == "iOS"
            assert mails_testing.outbox[0]["params"]["SOURCE"] == "iPhone 13"
            assert mails_testing.outbox[0]["params"]["LOGIN_DATE"]
            assert mails_testing.outbox[0]["params"]["LOGIN_TIME"]
            assert mails_testing.outbox[0]["params"]["ACCOUNT_SECURING_LINK"]

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_send_limited_number_of_emails_when_login_is_suspicious(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_google_oauth.return_value = self.valid_google_user
            users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True)

            for _ in range(users_constants.MAX_SUSPICIOUS_LOGIN_EMAILS + 1):
                data = copy.deepcopy(data)
                data["deviceInfo"]["deviceId"] = str(uuid.uuid4()).upper()
                client.post(f"/native/v1/{signin_route}", json=data, headers=self.headers)

            assert len(mails_testing.outbox) == users_constants.MAX_SUSPICIOUS_LOGIN_EMAILS

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_send_suspicious_login_email_to_user_suspended_upon_request(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            user = users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD)
            history_factories.SuspendedUserActionHistoryFactory(
                user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
            )

            client.post(f"/native/v1/{signin_route}", json=data, headers=self.headers)

            assert len(mails_testing.outbox) == 1
            assert mails_testing.outbox[0]["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        @pytest.mark.parametrize(
            "reason",
            [
                users_constants.SuspensionReason.FRAUD_SUSPICION,
                users_constants.SuspensionReason.FRAUD_HACK,
                users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP,
                users_constants.SuspensionReason.FRAUD_USURPATION,
            ],
        )
        def should_not_send_suspicious_login_email_to_suspended_user(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data, reason
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            user = users_factories.UserFactory(
                email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=False
            )
            history_factories.SuspendedUserActionHistoryFactory(user=user, reason=reason)

            client.post(f"/native/v1/{signin_route}", json=data, headers=self.headers)

            assert len(mails_testing.outbox) == 0

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_extend_refresh_token_lifetime_when_logging_in_with_a_trusted_device(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            user = users_factories.UserFactory(
                email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True
            )
            users_factories.TrustedDeviceFactory(user=user, deviceId=data["deviceInfo"]["deviceId"])

            response = client.post(f"/native/v1/{signin_route}", json=data)

            decoded_refresh_token = decode_token(response.json["refreshToken"])
            token_issue_date = decoded_refresh_token["iat"]
            token_expiration_date = decoded_refresh_token["exp"]
            refresh_token_lifetime = token_expiration_date - token_issue_date

            assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_not_extend_refresh_token_lifetime_when_logging_in_from_unknown_device(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True)

            response = client.post(f"/native/v1/{signin_route}", json=data)

            decoded_refresh_token = decode_token(response.json["refreshToken"])
            token_issue_date = decoded_refresh_token["iat"]
            token_expiration_date = decoded_refresh_token["exp"]
            refresh_token_lifetime = token_expiration_date - token_issue_date

            assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(
            WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=True, WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=False
        )
        def should_not_send_email_when_logging_in_from_a_trusted_device(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            user = users_factories.UserFactory(
                email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True
            )
            users_factories.TrustedDeviceFactory(user=user)

            client.post(f"/native/v1/{signin_route}", json=data)

            assert len(mails_testing.outbox) == 0

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(WIP_ENABLE_GOOGLE_SSO=True, WIP_ENABLE_TRUSTED_DEVICE=False)
        def should_not_send_email_when_feature_flag_is_inactive(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True)

            client.post(f"/native/v1/{signin_route}", json=data)

            assert len(mails_testing.outbox) == 0

        @patch("pcapi.core.token.UUIDToken.load_and_check")
        @patch("pcapi.connectors.google_oauth.get_google_user")
        @override_features(
            WIP_ENABLE_GOOGLE_SSO=True,
            WIP_ENABLE_TRUSTED_DEVICE=True,
            WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=False,
        )
        def should_not_send_email_when_feature_flag_is_active_but_email_is_inactive(
            self, mocked_google_oauth, mocked_load_and_check_oauth_token, client, signin_route, data
        ):
            mocked_load_and_check_oauth_token.return_value = self.valid_oauth_state_token
            mocked_google_oauth.return_value = self.valid_google_user
            users_factories.UserFactory(email="user@test.com", password=settings.TEST_DEFAULT_PASSWORD, isActive=True)

            client.post(f"/native/v1/{signin_route}", json=data)

            assert len(mails_testing.outbox) == 0

    class TrustedDeviceEmailValidationTest:
        @override_features(WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_extend_refresh_token_lifetime_on_email_validation_when_device_is_trusted(self, client):
            device_info = {
                "deviceId": "2E429592-2446-425F-9A62-D6983F375B3B",
                "source": "iPhone 13",
                "os": "iOS",
            }
            user = users_factories.UserFactory(isEmailValidated=False)
            users_factories.TrustedDeviceFactory(user=user, deviceId=device_info["deviceId"])
            token = token_utils.Token.create(
                type_=token_utils.TokenType.EMAIL_VALIDATION,
                ttl=users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
                user_id=user.id,
            ).encoded_token

            response = client.post(
                "/native/v1/validate_email",
                json={"email_validation_token": token, "deviceInfo": device_info},
            )

            decoded_refresh_token = decode_token(response.json["refreshToken"])
            token_issue_date = decoded_refresh_token["iat"]
            token_expiration_date = decoded_refresh_token["exp"]
            refresh_token_lifetime = token_expiration_date - token_issue_date

            assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES

        @override_features(WIP_ENABLE_TRUSTED_DEVICE=True)
        def should_not_extend_refresh_token_lifetime_on_email_validation_when_device_is_unknown(self, client):
            user = users_factories.UserFactory(isEmailValidated=False)
            token = token_utils.Token.create(
                type_=token_utils.TokenType.EMAIL_VALIDATION,
                ttl=users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
                user_id=user.id,
            ).encoded_token

            response = client.post("/native/v1/validate_email", json={"email_validation_token": token})

            decoded_refresh_token = decode_token(response.json["refreshToken"])
            token_issue_date = decoded_refresh_token["iat"]
            token_expiration_date = decoded_refresh_token["exp"]
            refresh_token_lifetime = token_expiration_date - token_issue_date

            assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES


class RequestResetPasswordTest:
    def test_send_reset_password_email_without_email(self, client):
        response = client.post(
            "/native/v1/request_password_reset",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert response.json["email"] == ["Ce champ est obligatoire"]

    def test_request_reset_password_for_unknown_email(self, client):
        data = {"email": "not_existing_user@example.com"}
        response = client.post("/native/v1/request_password_reset", json=data)

        assert response.status_code == 204

    @patch("pcapi.connectors.api_recaptcha.check_native_app_recaptcha_token")
    @override_features(ENABLE_NATIVE_APP_RECAPTCHA=True)
    def test_request_reset_password_with_recaptcha_ok(
        self,
        mock_check_native_app_recaptcha_token,
        client,
    ):
        email = "existing_user@example.com"
        data = {"email": email}
        user = users_factories.UserFactory(email=email)

        mock_check_native_app_recaptcha_token.return_value = None

        response = client.post("/native/v1/request_password_reset", json=data)

        mock_check_native_app_recaptcha_token.assert_called_once()
        assert response.status_code == 204

        assert token_utils.Token.token_exists(token_utils.TokenType.RESET_PASSWORD, user.id)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"]["RESET_PASSWORD_LINK"]

    def test_request_reset_password_for_existing_email(self, client):
        email = "existing_user@example.com"
        data = {"email": email}
        user = users_factories.UserFactory(email=email)

        response = client.post("/native/v1/request_password_reset", json=data)

        assert response.status_code == 204

        assert token_utils.Token.token_exists(token_utils.TokenType.RESET_PASSWORD, user.id)
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"]["RESET_PASSWORD_LINK"]

    def test_reset_password_with_not_valid_token(self, client):
        data = {"reset_password_token": "unknown_token", "new_password": "new_password"}
        user = users_factories.UserFactory()
        old_password = user.password

        response = client.post("/native/v1/reset_password", json=data)

        assert response.status_code == 400
        assert user.password == old_password

    def test_reset_password_success(self, client):
        new_password = "New_password1998!"

        user = users_factories.UserFactory()
        token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, users_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user_id=user.id
        )

        data = {"reset_password_token": token.encoded_token, "new_password": new_password}
        response = client.post("/native/v1/reset_password", json=data)

        assert response.status_code == 200
        db.session.refresh(user)
        assert user.password == crypto.hash_password(new_password)

        with pytest.raises(users_exceptions.InvalidToken):
            token.check(token_utils.TokenType.RESET_PASSWORD)
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

    @patch("pcapi.core.subscription.dms.api.try_dms_orphan_adoption")
    def test_reset_password_for_unvalidated_email(self, try_dms_orphan_adoption_mock, client):
        new_password = "New_password1998!"

        user = users_factories.UserFactory(isEmailValidated=False)
        token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, users_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user_id=user.id
        )

        data = {"reset_password_token": token.encoded_token, "new_password": new_password}
        response = client.post("/native/v1/reset_password", json=data)

        assert response.status_code == 200
        db.session.refresh(user)
        assert user.password == crypto.hash_password(new_password)
        try_dms_orphan_adoption_mock.assert_called_once_with(user)
        assert user.isEmailValidated

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

    def test_reset_password_fail_for_password_strength(self, client):
        user = users_factories.UserFactory()
        token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, users_constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user_id=user.id
        )

        old_password = user.password
        new_password = "weak_password"

        data = {"reset_password_token": token.encoded_token, "new_password": new_password}

        response = client.post("/native/v1/reset_password", json=data)

        assert response.status_code == 400
        db.session.refresh(user)
        assert user.password == old_password
        # should note raise
        token.check(token_utils.TokenType.RESET_PASSWORD)

    def test_change_password_success(self, client):
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

    def test_change_password_failures(self, client):
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

    def test_change_password_failure_when_user_has_no_password(self, client):
        user = users_factories.UserFactory(password=None)

        access_token = create_access_token(identity=user.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = client.post(
            "/native/v1/change_password",
            json={"currentPassword": "", "newPassword": "New_password1998!"},
        )

        assert response.status_code == 400
        assert response.json["code"] == "NO_CURRENT_PASSWORD"


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

        assert token_utils.Token.token_exists(token_utils.TokenType.RESET_PASSWORD, user.id)
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"]["RESET_PASSWORD_LINK"]


class EmailValidationTest:
    def initialize_token(self, user, is_expired=False):
        token = token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_VALIDATION,
            ttl=users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
            user_id=user.id,
        )
        if is_expired:
            token.expire()
        return token.encoded_token

    def test_validate_email_with_expired_token(self, client):
        user = users_factories.UserFactory(isEmailValidated=False)
        token = self.initialize_token(
            user=user,
            is_expired=True,
        )

        response = client.post("/native/v1/validate_email", json={"email_validation_token": token})

        assert response.status_code == 400

    @time_machine.travel("2018-06-01")
    def test_validate_email_when_eligible(self, client):
        user = users_factories.UserFactory(
            isEmailValidated=False,
            dateOfBirth=datetime(2000, 6, 1),
        )
        token = self.initialize_token(user)

        response = client.post("/native/v1/validate_email", json={"email_validation_token": token})

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

    def test_validate_email_second_time_is_forbidden(self, client):
        user = users_factories.UserFactory(isEmailValidated=False)
        token = self.initialize_token(user)

        response = client.post("/native/v1/validate_email", json={"email_validation_token": token})

        assert user.isEmailValidated
        assert response.status_code == 200

        response = client.post("/native/v1/validate_email", json={"email_validation_token": token})
        assert response.status_code == 400
        assert response.json["token"] == ["Le token de validation d'email est invalide."]

    @time_machine.travel("2018-06-01")
    def test_validate_email_when_not_eligible(self, client):
        user = users_factories.UserFactory(isEmailValidated=False, dateOfBirth=datetime(2000, 7, 1))
        token = self.initialize_token(user)

        assert not user.isEmailValidated

        response = client.post("/native/v1/validate_email", json={"email_validation_token": token})

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
    def test_validate_email_dms_orphan(self, execute_query, client):
        application_number = 1234
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(isEmailValidated=False, dateOfBirth=datetime(2000, 7, 1), email=email)
        token = self.initialize_token(user)

        assert not user.isEmailValidated

        fraud_factories.OrphanDmsApplicationFactory(email=email, application_id=application_number)

        execute_query.return_value = make_single_application(
            application_number, dms_models.GraphQLApplicationStates.accepted, email=email
        )
        response = client.post("/native/v1/validate_email", json={"email_validation_token": token})

        assert user.isEmailValidated
        assert response.status_code == 200

        fraud_check = subscription_api.get_relevant_identity_fraud_check(user, user.eligibility)
        assert fraud_check is not None
