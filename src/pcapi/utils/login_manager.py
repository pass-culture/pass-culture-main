""" login_manager """
import logging
import uuid

from flask import current_app as app
from flask import jsonify
from flask import session

from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.user_session_queries import delete_user_session
from pcapi.repository.user_session_queries import existing_user_session
from pcapi.repository.user_session_queries import register_user_session


logger = logging.getLogger(__name__)


@app.login_manager.user_loader
def get_user_with_id(user_id):
    session.permanent = True
    session_uuid = session.get("session_uuid")
    if existing_user_session(user_id, session_uuid):
        return User.query.get(user_id)
    return None


@app.login_manager.unauthorized_handler
def send_401():
    e = ApiErrors()
    e.add_error("global", "Authentification nécessaire")
    return jsonify(e.errors), 401


def stamp_session(user):
    session_uuid = uuid.uuid4()
    session["session_uuid"] = session_uuid
    session["user_id"] = user.id
    register_user_session(user.id, session_uuid)


def discard_session():
    session_uuid = session.get("session_uuid")
    user_id = session.get("user_id")
    session.clear()
    delete_user_session(user_id, session_uuid)
