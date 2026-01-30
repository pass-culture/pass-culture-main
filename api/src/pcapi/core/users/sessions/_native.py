from dataclasses import dataclass
from enum import StrEnum

import flask
from flask_jwt_extended import verify_jwt_in_request

from pcapi.core.users import models as users_models
from pcapi.models import db

from . import _common


class JwtType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass
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
