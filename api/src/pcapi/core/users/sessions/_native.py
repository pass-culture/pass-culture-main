import enum
import typing
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta

import flask
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import verify_jwt_in_request

from pcapi import settings
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils

from . import _common


if typing.TYPE_CHECKING:
    from pcapi.routes.native.v1.serialization import account as account_serialization


@dataclass(frozen=True, slots=True)
class TokensContainer:
    access: str
    refresh: str


class JwtType(enum.StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True, slots=True)
class JwtData:
    fresh: bool
    iat: datetime
    jti: str
    type: JwtType
    sub: str
    nbf: datetime
    csrf: str
    exp: datetime
    user_claims: dict | None = None


@dataclass(frozen=True, slots=True)
class JwtContainer:
    data: JwtData
    raw: str


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
        jwt = load_jwt(request, jwt_type=JwtType.ACCESS)

        if jwt is None:
            # invalid token
            return None

        if jwt.data.user_claims is None:
            # refresh token
            return None

        return (
            db.session.query(users_models.User)
            .filter(users_models.User.id == jwt.data.user_claims["user_id"])
            .one_or_none()
        )


def load_jwt(request: flask.Request, *, jwt_type: JwtType) -> JwtContainer | None:
    _delete_jwt_container()
    try:
        results = verify_jwt_in_request(optional=False, verify_type=True, refresh=(jwt_type == JwtType.REFRESH))
    except Exception:
        # if any problem is detected the authentication is invalid
        return None

    if not results:
        # helps mypy. This should not be possible
        return None

    return save_jwt_container(results, request)


def _is_used_jwt_refresh() -> bool:
    return hasattr(flask.g, "jwt") and flask.g.jwt.data.type == JwtType.REFRESH


def save_jwt_container(data: tuple[dict, dict], request: flask.Request) -> JwtContainer:
    raw = request.headers.get("Authorization", " ").split(" ")[1]

    unsigned_data, signed_data = data

    flask.g.jwt = JwtContainer(
        raw=raw,
        data=JwtData(
            fresh=signed_data["fresh"],
            iat=datetime.fromtimestamp(signed_data["iat"]),
            jti=signed_data["jti"],
            type=JwtType(signed_data["type"].lower()),
            sub=signed_data["sub"],
            nbf=datetime.fromtimestamp(signed_data["nbf"]),
            csrf=signed_data["csrf"],
            exp=datetime.fromtimestamp(signed_data["exp"]),
            user_claims=signed_data.get("user_claims", None),
        ),
    )
    return flask.g.jwt


def _delete_jwt_container() -> None:
    if hasattr(flask.g, "jwt"):
        del flask.g.jwt


def create_user_jwt_tokens(
    user: users_models.User,
    device_info: "account_serialization.TrustedDevice | None" = None,
) -> TokensContainer:
    if _is_used_jwt_refresh():
        # TODO regenerate a refresh token when renewing the access token
        refresh_token = flask.g.jwt.raw
    else:
        if users_api.is_login_device_a_trusted_device(device_info, user):
            duration = timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES)
        else:
            duration = timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES)
        refresh_token = create_refresh_token(identity=user.email, expires_delta=duration)

    access_token = create_access_token(identity=user.email, additional_claims={"user_claims": {"user_id": user.id}})
    return TokensContainer(access=access_token, refresh=refresh_token)


def delete_expired_jwt() -> None:
    db.session.query(users_models.NativeUserSession).filter(
        users_models.NativeUserSession.expirationDatetime < date_utils.get_naive_utc_now()
    ).delete(synchronize_session=False)
