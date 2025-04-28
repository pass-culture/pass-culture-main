from datetime import datetime
from datetime import timedelta
import logging
import os
import signal
import uuid

import flask
from flask import current_app as app
from flask_login import logout_user
from sqlalchemy.exc import InternalError
import werkzeug.datastructures

import pcapi.core.users.backoffice.api as backoffice_api
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.backoffice.blueprint import backoffice_web
from pcapi.routes.pro.blueprint import pro_private_api


logger = logging.getLogger(__name__)

PRO_APIS = {pro_private_api.name, private_api.name}
PRO_SESSION_GRACE_TIME = timedelta(hours=1)
PRO_SESSION_BASE_TIMEOUT = timedelta(days=45)
PRO_SESSION_LOGIN_TIMEOUT = timedelta(days=90)
PRO_SESSION_FORCE_TIMEOUT = timedelta(days=91)


def get_request_authorization() -> werkzeug.datastructures.Authorization | None:
    try:
        return flask.request.authorization
    except UnicodeDecodeError:
        # `werkzeug.http.parse_authorization_header()` raises a
        # UnicodeDecodeError if the login or the password contains
        # characters that have not been encoded in "utf-8", which
        # we'll happily send to Sentry, where the password could
        # appear as clear text.
        return None


@app.login_manager.user_loader  # type: ignore[attr-defined]
def get_user_with_id(user_id: str) -> users_models.User | None:
    if flask.request.path.startswith("/static/"):
        # No DB request to serve static files
        return None

    flask.session.permanent = True
    session_uuid = flask.session.get("session_uuid")
    try:
        user_session = (
            db.session.query(users_models.UserSession).filter_by(userId=user_id, uuid=session_uuid).one_or_none()
        )
    except InternalError as exception:
        logger.error(
            "The connection seems corrupted, killing the worker (SIGINT)",
            extra={
                "exc": str(exception),
            },
            exc_info=True,
        )
        os.kill(os.getpid(), signal.SIGINT)

    if not user_session:
        return None

    try:
        if flask.request.blueprint.startswith(backoffice_web.name):  # type: ignore[union-attr]
            return backoffice_api.fetch_user_with_profile(int(user_id))
    except AttributeError:
        pass

    user = db.session.query(users_models.User).filter(users_models.User.id == user_id).one_or_none()

    internal_admin_id = flask.session.get("internal_admin_id", 0)
    if user and internal_admin_id:
        if admin := db.session.query(users_models.User).filter(users_models.User.id == internal_admin_id).one_or_none():
            user.impersonator = admin
    return manage_pro_session(user)


@app.login_manager.unauthorized_handler  # type: ignore[attr-defined]
def send_401() -> tuple[flask.Response, int]:
    e = ApiErrors()
    e.add_error("global", "Authentification nécessaire")
    return flask.jsonify(e.errors), 401


def stamp_session(user: users_models.User) -> None:
    session_uuid = uuid.uuid4()
    flask.session["session_uuid"] = session_uuid
    flask.session["user_id"] = user.id
    db.session.add(users_models.UserSession(userId=user.id, uuid=session_uuid))
    db.session.commit()


def discard_session() -> None:
    session_uuid = flask.session.get("session_uuid")
    user_id = flask.session.get("user_id")
    flask.session.clear()
    db.session.query(users_models.UserSession).filter_by(
        userId=user_id,
        uuid=session_uuid,
    ).delete(synchronize_session=False)
    db.session.commit()


def manage_pro_session(user: users_models.User | None) -> users_models.User | None:
    if not user:
        return None
    if not user.has_any_pro_role:
        return user

    if getattr(flask.request, "blueprint", "") not in PRO_APIS:
        return user

    current_timestamp = datetime.utcnow().timestamp()
    last_login = datetime.fromtimestamp(flask.session.get("last_login", current_timestamp))
    last_api_call = datetime.fromtimestamp(flask.session.get("last_api_call", current_timestamp))

    valid_session = compute_pro_session_validity(last_login, last_api_call)

    if "last_login" not in flask.session:
        flask.session["last_login"] = current_timestamp
    flask.session["last_api_call"] = current_timestamp

    if valid_session:
        return user

    discard_session()
    logout_user()
    return None


def compute_pro_session_validity(last_login: datetime, last_api_call: datetime) -> bool:
    now = datetime.utcnow()

    if last_api_call + PRO_SESSION_BASE_TIMEOUT < now:
        return False

    if last_login + PRO_SESSION_LOGIN_TIMEOUT > now:
        return True

    if last_api_call + PRO_SESSION_GRACE_TIME < now:
        return False

    if last_login + PRO_SESSION_FORCE_TIMEOUT > now:
        return True

    return False
