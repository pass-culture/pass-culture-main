import abc
from datetime import timedelta
from enum import Enum
from uuid import UUID

import flask

from pcapi import settings
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.utils import date as date_utils


NATIVE_FOLDERS = {
    "/native/",
    "/saml/educonnect/",
}


class Origin(Enum):
    BACKOFFICE = "BACKOFFICE"
    NATIVE = "NATIVE"
    PRO = "PRO"


class AbstractSessionManager(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def stamp_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def discard_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def request_loader(request: flask.Request) -> users_models.User | None:
        raise NotImplementedError


class ForbiddenOrigin(Exception):
    pass


def get_origin() -> Origin:
    if flask.request.host == settings.BACKOFFICE_URL:
        return Origin.BACKOFFICE
    for native_folder in NATIVE_FOLDERS:
        if flask.request.path.startswith(native_folder):
            return Origin.NATIVE
    return Origin.PRO


def stamp_session(*, origin: Origin, user_id: int, duration: timedelta, session_uuid: UUID) -> None:
    flask.session["user_id"] = user_id
    db.session.add(
        users_models.UserSession(
            userId=user_id,
            uuid=session_uuid,
            expirationDatetime=date_utils.get_naive_utc_now() + duration,
        )
    )


def discard_session(*, origin: Origin, session_uuid: UUID | None) -> None:
    if session_uuid:
        db.session.query(users_models.UserSession).filter_by(
            uuid=session_uuid,
        ).delete()


def unauthorized_handler() -> tuple[flask.Response, int]:
    e = ApiErrors()
    e.add_error("global", "Authentification nécessaire")
    return flask.jsonify(e.errors), 401


def get_user_from_session(
    user_id: str | None, session_uuid: str | None, session_type: Origin, options: tuple = tuple()
) -> users_models.User | None:
    if not user_id or not session_uuid:
        return None

    query = (
        db.session.query(users_models.User)
        .join(users_models.UserSession, users_models.User.id == users_models.UserSession.userId)
        .filter(
            users_models.UserSession.userId == int(user_id),
            users_models.UserSession.uuid == session_uuid,
            users_models.UserSession.expirationDatetime > date_utils.get_naive_utc_now(),
        )
    )
    if options:
        query = query.options(*options)

    return query.one_or_none()
