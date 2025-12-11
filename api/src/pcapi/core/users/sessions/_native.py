from dataclasses import dataclass

import flask
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import WrongTokenError

from pcapi.core.users import models as users_models
from pcapi.models import db

from . import _common


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
    user_claims: dict


class SessionManager(_common.AbstractSessionManager):
    @staticmethod
    def stamp_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
        return None

    @staticmethod
    def discard_session(app: flask.ctx.AppContext | None = None, user: users_models.User | None = None) -> None:
        return None

    @staticmethod
    def request_loader(request: flask.Request) -> users_models.User | None:
        try:
            result = verify_jwt_in_request(
                refresh=False,
                verify_type=True,
                optional=True,
            )
        except WrongTokenError:
            return None

        if not result:
            # invalid jwt or jwt type or no jwt
            return None

        jwt_data = JwtData(**result[1])
        flask.g.jwt_data = jwt_data

        return (
            db.session.query(users_models.User)
            .filter(users_models.User.id == jwt_data.user_claims["user_id"])
            .one_or_none()
        )
