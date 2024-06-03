import uuid

import flask
from flask import current_app as app
import werkzeug.datastructures

import pcapi.core.users.backoffice.api as backoffice_api
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.backoffice.blueprint import backoffice_web


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
    flask.session.permanent = True
    session_uuid = flask.session.get("session_uuid")
    if not users_models.UserSession.query.filter_by(userId=user_id, uuid=session_uuid).one_or_none():
        return None

    try:
        if flask.request.blueprint.startswith(backoffice_web.name):  # type: ignore[union-attr]
            return backoffice_api.fetch_user_with_profile(int(user_id))
    except AttributeError:
        pass

    user = users_models.User.query.filter(users_models.User.id == user_id).one_or_none()

    internal_admin_id = flask.session.get("internal_admin_id", 0)
    if user and internal_admin_id:
        if admin := users_models.User.query.filter(users_models.User.id == internal_admin_id).one_or_none():
            user.impersonator = admin
    return user


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
    users_models.UserSession.query.filter_by(
        userId=user_id,
        uuid=session_uuid,
    ).delete(synchronize_session=False)
    db.session.commit()
