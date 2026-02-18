import enum
import typing
from dataclasses import dataclass
from datetime import timedelta

import flask
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import verify_jwt_in_request

from pcapi import settings
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import db

from . import _common


if typing.TYPE_CHECKING:
    from pcapi.routes.native.v1.serialization import account as account_serialization


@dataclass(frozen=True, slots=True)
class JwtContainer:
    access: str
    refresh: str


class JwtType(enum.StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True, slots=True)
class JwtData:
    fresh: bool
    iat: int
    jti: str
    type: str
    sub: str
    nbf: int
    csrf: str
    exp: int
    user_claims: dict | None = None


class SessionManager(_common.AbstractSessionManager):
    @staticmethod
    def stamp_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
        # called every time a user connects or renew their token
        return None

    @staticmethod
    def discard_session(app: flask.ctx.AppContext | None = None, user: users_models.User | None = None) -> None:
        return None

    @staticmethod
    def request_loader(request: flask.Request) -> users_models.User | None:
        jwt_data = load_jwt(request, jwt_type=JwtType.ACCESS)

        if jwt_data is None:
            # invalid token
            return None

        if jwt_data.user_claims is None:
            # refresh token
            return None

        return (
            db.session.query(users_models.User)
            .filter(users_models.User.id == jwt_data.user_claims["user_id"])
            .one_or_none()
        )


def load_jwt(request: flask.Request, *, jwt_type: JwtType) -> JwtData | None:
    _clean_previously_loaded_token()
    try:
        result = verify_jwt_in_request(optional=False, verify_type=True, refresh=(jwt_type == JwtType.REFRESH))
    except Exception:
        # if any problem is detected the authentication is invalid
        return None

    if not result:
        # helps mypy. This should not be possible
        return None

    jwt_data = JwtData(**result[1])

    flask.g.jwt_data = jwt_data
    flask.g.raw_jwt = request.headers.get("Authorization", " ").split(" ")[1]

    return jwt_data


def _clean_previously_loaded_token() -> None:
    if hasattr(flask.g, "jwt_data"):
        del flask.g.jwt_data
    if hasattr(flask.g, "raw_jwt"):
        del flask.g.raw_jwt


def _is_used_jwt_refresh() -> bool:
    return (
        hasattr(flask.g, "jwt_data") and hasattr(flask.g, "raw_jwt") and flask.g.jwt_data.type == JwtType.REFRESH.value
    )


def create_user_jwt_tokens(
    user: users_models.User,
    device_info: "account_serialization.TrustedDevice | None" = None,
) -> JwtContainer:
    if _is_used_jwt_refresh():
        # TODO regenerate a refresh token when renewing the access token
        refresh_token = flask.g.raw_jwt
    else:
        if users_api.is_login_device_a_trusted_device(device_info, user):
            duration = timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES)
        else:
            duration = timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES)
        refresh_token = create_refresh_token(identity=user.email, expires_delta=duration)

    access_token = create_access_token(identity=user.email, additional_claims={"user_claims": {"user_id": user.id}})
    return JwtContainer(access=access_token, refresh=refresh_token)
