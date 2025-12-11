import uuid
from datetime import datetime

import flask
import flask_login

from pcapi import settings
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import is_managed_transaction

from . import _common


class SessionManager(_common.AbstractSessionManager):
    @staticmethod
    def stamp_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
        if old_uuid := flask.session.get("session_uuid", None):
            _common.discard_session(
                origin=_common.Origin.PRO,
                session_uuid=old_uuid,
            )
        flask.session["session_uuid"] = uuid.uuid4()
        flask.session["last_login"] = date_utils.get_naive_utc_now().timestamp()
        _common.stamp_session(
            duration=settings.PRO_SESSION_FORCE_TIMEOUT_IN_DAYS,
            origin=_common.Origin.PRO,
            session_uuid=flask.session["session_uuid"],
            user_id=user.id,
        )

        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()

    @staticmethod
    def discard_session(app: flask.ctx.AppContext | None = None, user: users_models.User | None = None) -> None:
        _common.discard_session(
            origin=_common.Origin.PRO,
            session_uuid=flask.session.get("session_uuid", None),
        )
        flask.session.clear()

        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()

    @staticmethod
    def request_loader(request: flask.Request) -> users_models.User | None:
        user_id = flask.session.get("user_id")
        user = None
        if user_id:
            session_uuid = flask.session.get("session_uuid")
            user = _common.get_user_from_session(
                user_id=user_id,
                session_uuid=session_uuid,
                session_type=_common.Origin.PRO,
            )
        if not user:
            return None

        # persist session in the client's cookies
        flask.session.permanent = True
        internal_admin_id = flask.session.get("internal_admin_id", 0)
        if user and internal_admin_id:
            if (
                admin := db.session.query(users_models.User)
                .filter(users_models.User.id == internal_admin_id)
                .one_or_none()
            ):
                user.impersonator = admin
        return manage_pro_session(user)


def manage_pro_session(user: users_models.User | None) -> users_models.User | None:
    if not user:
        return None

    current_timestamp = date_utils.get_naive_utc_now().timestamp()
    last_login = datetime.fromtimestamp(flask.session.get("last_login", current_timestamp))
    last_api_call = datetime.fromtimestamp(flask.session.get("last_api_call", current_timestamp))

    valid_session = compute_pro_session_validity(last_login, last_api_call)

    if "last_login" not in flask.session:
        flask.session["last_login"] = current_timestamp
    flask.session["last_api_call"] = current_timestamp

    if valid_session:
        return user

    flask_login.logout_user()
    return None


def compute_pro_session_validity(last_login: datetime, last_api_call: datetime) -> bool:
    now = date_utils.get_naive_utc_now()

    if last_login + settings.PRO_SESSION_LOGIN_TIMEOUT_IN_DAYS > now:  # connected less than 14 days ago
        return True

    if (
        last_api_call + settings.PRO_SESSION_GRACE_TIME_IN_HOURS < now
    ):  # connected more than 14 days ago and did not do anything in the last hour
        return False

    if (
        last_login + settings.PRO_SESSION_FORCE_TIMEOUT_IN_DAYS > now
    ):  # connected more than 14 days ago BUT less than 15 days ago, did something in the last hour
        return True

    return False
