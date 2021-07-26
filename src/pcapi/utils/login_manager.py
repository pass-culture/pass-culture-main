""" login_manager """
import logging
import uuid

from flask import current_app as app
from flask import jsonify
from flask import session
from flask_login import login_user

from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import repository as users_repo
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


@app.login_manager.request_loader
def get_user_with_request(request):
    auth = request.authorization
    if not auth:
        return None
    errors = ApiErrors()
    errors.status_code = 401
    try:
        user = users_repo.get_user_with_credentials(auth.username, auth.password)
    except users_exceptions.InvalidIdentifier as exc:
        errors.add_error("identifier", "Identifiant ou mot de passe incorrect")
        raise errors from exc
    except users_exceptions.UnvalidatedAccount as exc:
        errors.add_error("identifier", "Ce compte n'est pas validé.")
        raise errors from exc
    logger.info("User logged in with authorization header", extra={"route": str(request.url_rule)})
    login_user(user)
    stamp_session(user)
    return user


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
