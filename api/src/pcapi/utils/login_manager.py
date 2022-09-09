""" login_manager """
import logging
import uuid

from flask import current_app as app
from flask import jsonify
from flask import request
from flask import session

import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors


logger = logging.getLogger(__name__)


def get_request_authorization():  # type: ignore [no-untyped-def]
    try:
        return request.authorization
    except UnicodeDecodeError:
        # `werkzeug.http.parse_authorization_header()` raises a
        # UnicodeDecodeError if the login or the password contains
        # characters that have not been encoded in "utf-8", which
        # we'll happily send to Sentry, where the password could
        # appear as clear text.
        return None


@app.login_manager.user_loader  # type: ignore [attr-defined]
def get_user_with_id(user_id: int) -> None:
    session.permanent = True
    session_uuid = session.get("session_uuid")
    if users_models.UserSession.query.filter_by(userId=user_id, uuid=session_uuid).one_or_none():
        return users_models.User.query.get(user_id)
    return None


@app.login_manager.unauthorized_handler  # type: ignore [attr-defined]
def send_401():  # type: ignore [no-untyped-def]
    e = ApiErrors()
    e.add_error("global", "Authentification nécessaire")
    return jsonify(e.errors), 401


def stamp_session(user: users_models.User) -> None:
    session_uuid = uuid.uuid4()
    session["session_uuid"] = session_uuid
    session["user_id"] = user.id
    db.session.add(users_models.UserSession(userId=user.id, uuid=session_uuid))
    db.session.commit()


def discard_session() -> None:
    session_uuid = session.get("session_uuid")
    user_id = session.get("user_id")
    session.clear()
    users_models.UserSession.query.filter_by(
        userId=user_id,
        uuid=session_uuid,
    ).delete(synchronize_session=False)
    db.session.commit()
