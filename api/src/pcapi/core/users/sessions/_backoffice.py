import uuid
from datetime import timedelta

import flask
import flask_login
from sqlalchemy import orm as sa_orm

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db

from . import _common


# a french worker cannot work for more than 12 hours so disconnecting them after 13 hours is safe
MAXIMUM_SESSION_LENGTH_HOURS = 13


def install_login() -> None:
    login_manager = flask_login.LoginManager()
    login_manager.init_app(flask.current_app)
    login_manager.unauthorized_handler(_common.unauthorized_handler)
    login_manager.user_loader(user_loader)
    flask_login.user_logged_in.connect(stamp_session)
    flask_login.user_logged_out.connect(discard_session)


def stamp_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
    if old_uuid := flask.session.get("session_uuid", None):
        # drop previous session if it existed
        _common.discard_session(
            origin=_common.Origin.PRO,
            session_uuid=old_uuid,
        )
    flask.session["session_uuid"] = uuid.uuid4()
    _common.stamp_session(
        duration=timedelta(hours=MAXIMUM_SESSION_LENGTH_HOURS),
        origin=_common.Origin.BACKOFFICE,
        session_uuid=flask.session["session_uuid"],
        user_id=user.id,
    )
    # we already are in an atomic transaction, just flush the session
    db.session.flush()


def discard_session(app: flask.ctx.AppContext | None = None, user: users_models.User | None = None) -> None:
    _common.discard_session(
        origin=_common.Origin.BACKOFFICE,
        session_uuid=flask.session.get("session_uuid", None),
    )
    flask.session.clear()
    # we already are in an atomic transaction, just flush the session
    db.session.flush()


def user_loader(user_id: str | None) -> users_models.User | None:
    if flask.request.path.startswith("/static/"):
        # No DB request to serve static files
        return None

    # persist session in the client's cookies
    flask.session.permanent = True
    session_uuid = flask.session.get("session_uuid")
    return _common.get_user_from_session(
        user_id=user_id,
        session_uuid=session_uuid,
        session_type=_common.Origin.BACKOFFICE,
        options=(
            sa_orm.joinedload(users_models.User.backoffice_profile)
            .joinedload(perm_models.BackOfficeUserProfile.roles)
            .joinedload(perm_models.Role.permissions),
            sa_orm.load_only(
                users_models.User.id,
                users_models.User.email,
                users_models.User.firstName,
                users_models.User.lastName,
                users_models.User.roles,
            ),
        ),
    )
