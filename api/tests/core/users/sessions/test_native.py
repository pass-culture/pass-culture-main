import flask
import pytest
from flask_jwt_extended.utils import decode_token

from pcapi import settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users.sessions import create_user_jwt_tokens
from pcapi.core.users.sessions._native import JwtData
from pcapi.routes.native.v1.serialization import account as account_serialization


pytestmark = pytest.mark.usefixtures("db_session")


class CreateUsetJwtTokensTestTest:
    def should_create_access_token_with_default_lifetime_when_no_device_info(self):
        user = users_factories.UserFactory()

        tokens = create_user_jwt_tokens(user=user, device_info=None)
        decoded_refresh_token = decode_token(tokens.refresh)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

    def should_create_access_token_with_default_lifetime_when_device_is_not_a_trusted_device(self):
        user = users_factories.UserFactory()
        users_factories.TrustedDeviceFactory(user=user)
        other_device = account_serialization.TrustedDevice(deviceId="other-device-id", os="iOS", source="iPhone 13")

        tokens = create_user_jwt_tokens(user=user, device_info=other_device)
        decoded_refresh_token = decode_token(tokens.refresh)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

    def should_create_access_token_with_extended_lifetime_when_device_is_a_trusted_device(self):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)
        device_info = account_serialization.TrustedDevice(
            deviceId=trusted_device.deviceId, os="iOS", source="iPhone 13"
        )

        tokens = create_user_jwt_tokens(user=user, device_info=device_info)
        decoded_refresh_token = decode_token(tokens.refresh)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES

    def test_refresh_token_returns_itself(self):
        user = users_factories.UserFactory()

        refresh_token = "some secret jwt token"
        flask.g.raw_jwt = refresh_token
        flask.g.jwt_data = JwtData(
            fresh=False,
            iat=123456789,
            jti="123-456-789-secret",
            type="refresh",
            sub="user@example.com",
            nbf=123456789,
            csrf="123-456-789-secret",
            exp=123456789,
            user_claims=None,
        )
        tokens = create_user_jwt_tokens(user=user, device_info=None)

        decoded_access_token = decode_token(tokens.access)
        token_issue_date = decoded_access_token["iat"]
        token_expiration_date = decoded_access_token["exp"]
        access_token_lifetime = token_expiration_date - token_issue_date

        assert tokens.refresh == refresh_token
        assert access_token_lifetime == settings.JWT_ACCESS_TOKEN_EXPIRES

    def test_access_token_contains_user_id_and_email(self):
        user = users_factories.UserFactory()

        tokens = create_user_jwt_tokens(user=user, device_info=None)

        decoded_access_token = decode_token(tokens.access)
        token_issue_date = decoded_access_token["iat"]
        token_expiration_date = decoded_access_token["exp"]
        access_token_lifetime = token_expiration_date - token_issue_date

        assert access_token_lifetime == settings.JWT_ACCESS_TOKEN_EXPIRES
        assert decoded_access_token["sub"] == user.email
        assert decoded_access_token["user_claims"]["user_id"] == user.id
