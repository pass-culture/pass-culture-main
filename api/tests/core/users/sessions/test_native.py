from datetime import datetime
from datetime import timedelta

import flask
import pytest
from flask_jwt_extended.utils import create_refresh_token
from flask_jwt_extended.utils import decode_token

from pcapi import settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.sessions import _native
from pcapi.core.users.sessions import create_user_jwt_tokens
from pcapi.core.users.sessions import refresh_user_jwt_tokens
from pcapi.models import db
from pcapi.routes.native.v1.serialization import common_models
from pcapi.utils.date import get_naive_utc_now


pytestmark = pytest.mark.usefixtures("db_session")


class CreateUserJwtTokensTestTest:
    def should_create_access_token_with_default_lifetime_when_no_device_info(self):
        user = users_factories.UserFactory()

        tokens = create_user_jwt_tokens(user=user, device_info=None)
        decoded_refresh_token = decode_token(tokens.refresh)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES
        assert db.session.query(users_models.NativeUserSession).count() == 1
        assert (
            db.session.query(users_models.NativeUserSession)
            .filter(
                users_models.NativeUserSession.userId == user.id,
                users_models.NativeUserSession.deviceId == "",
                users_models.NativeUserSession.accessToken == decode_token(tokens.access)["jti"],
                users_models.NativeUserSession.refreshToken == decoded_refresh_token["jti"],
                users_models.NativeUserSession.expirationDatetime
                == datetime.fromtimestamp(decoded_refresh_token["exp"]),
            )
            .count()
            == 1
        )

    def should_create_access_token_with_default_lifetime_when_device_is_not_a_trusted_device(self):
        user = users_factories.UserFactory()
        users_factories.TrustedDeviceFactory(user=user)
        other_device = common_models.DeviceInfo(deviceId="other-device-id", os="iOS", source="iPhone 13")

        tokens = create_user_jwt_tokens(user=user, device_info=other_device)
        decoded_refresh_token = decode_token(tokens.refresh)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES
        assert db.session.query(users_models.NativeUserSession).count() == 1
        assert (
            db.session.query(users_models.NativeUserSession)
            .filter(
                users_models.NativeUserSession.userId == user.id,
                users_models.NativeUserSession.deviceId == other_device.device_id,
            )
            .count()
            == 1
        )

    def should_create_access_token_with_extended_lifetime_when_device_is_a_trusted_device(self):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)
        device_info = common_models.DeviceInfo(deviceId=trusted_device.deviceId, os="iOS", source="iPhone 13")

        tokens = create_user_jwt_tokens(user=user, device_info=device_info)
        decoded_refresh_token = decode_token(tokens.refresh)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES


class RefreshUserJwtTokensTestTest:
    def test_legacy_refresh_token_returns_itself(self):
        user = users_factories.UserFactory()

        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        flask.g.jwt = _native.JwtContainer(
            raw=refresh_token,
            data=_native.JwtData(
                fresh=False,
                iat=get_naive_utc_now(),
                jti="123-456-789-secret",
                type=_native.JwtType.REFRESH,
                sub=user.id,
                nbf=get_naive_utc_now(),
                csrf="123-456-789-secret",
                exp=get_naive_utc_now() + timedelta(days=30),
                user_claims=None,
            ),
        )
        tokens = refresh_user_jwt_tokens(user=user, device_info=None, legacy=True)

        decoded_access_token = decode_token(tokens.access)
        decoded_refresh_token = decode_token(tokens.refresh)

        assert tokens.refresh == refresh_token
        assert decoded_access_token["exp"] - decoded_access_token["nbf"] == settings.JWT_ACCESS_TOKEN_EXPIRES
        assert db.session.query(users_models.NativeUserSession).count() == 1
        assert (
            db.session.query(users_models.NativeUserSession)
            .filter(
                users_models.NativeUserSession.accessToken == decoded_access_token["jti"],
                users_models.NativeUserSession.refreshToken == decoded_refresh_token["jti"],
            )
            .count()
            == 1
        )

    def test_refresh_token_delete_old_token(self):
        device_info = common_models.DeviceInfo(deviceId="other-device-id", os="iOS", source="iPhone 13")
        user = users_factories.UserFactory()

        old_refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        decoded_old_refresh_token = decode_token(old_refresh_token)
        users_factories.NativeUserSessionFactory(
            user=user, accessToken="unused", refreshToken=decoded_old_refresh_token["jti"]
        )

        flask.g.jwt = _native.JwtContainer(
            raw=old_refresh_token,
            data=_native.JwtData(
                fresh=False,
                iat=datetime.fromtimestamp(decoded_old_refresh_token["iat"]),
                jti=decoded_old_refresh_token["jti"],
                type=_native.JwtType.REFRESH,
                sub=decoded_old_refresh_token["sub"],
                nbf=datetime.fromtimestamp(decoded_old_refresh_token["nbf"]),
                csrf=decoded_old_refresh_token["csrf"],
                exp=datetime.fromtimestamp(decoded_old_refresh_token["exp"]),
                user_claims=None,
            ),
        )
        tokens = refresh_user_jwt_tokens(user=user, device_info=device_info)

        decoded_access_token = decode_token(tokens.access)
        decoded_refresh_token = decode_token(tokens.refresh)

        assert decoded_refresh_token["jti"] != decoded_old_refresh_token["jti"]
        assert decoded_access_token["exp"] - decoded_access_token["nbf"] == settings.JWT_ACCESS_TOKEN_EXPIRES

        # the algorithm is not exact and the expiration time could chage by up to 1 second
        assert decoded_old_refresh_token["exp"] - 1 <= decoded_refresh_token["exp"]
        assert decoded_old_refresh_token["exp"] + 1 >= decoded_refresh_token["exp"]

        assert db.session.query(users_models.NativeUserSession).count() == 1
        assert (
            db.session.query(users_models.NativeUserSession)
            .filter(
                users_models.NativeUserSession.accessToken == decoded_access_token["jti"],
                users_models.NativeUserSession.refreshToken == decoded_refresh_token["jti"],
            )
            .count()
            == 1
        )


class DeleteExpiredJwtTest:
    def test_delete_expired_jwt(self):
        user = users_factories.BaseUserFactory()
        valid_session = users_factories.NativeUserSessionFactory(user=user)
        users_factories.NativeUserSessionFactory(user=user, expirationDatetime=get_naive_utc_now() - timedelta(days=1))

        _native.delete_expired_jwt()

        assert db.session.query(users_models.NativeUserSession).count() == 1
        assert db.session.query(users_models.NativeUserSession.id).scalar() == valid_session.id
