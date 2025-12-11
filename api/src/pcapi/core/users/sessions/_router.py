import flask
import flask_login

from pcapi.core.users import models as users_models

from . import _common
from . import _native
from . import _pro


def install_login() -> None:
    login_manager = flask_login.LoginManager()
    login_manager.init_app(flask.current_app)
    login_manager.unauthorized_handler(_common.unauthorized_handler)
    login_manager.request_loader(request_loader)
    flask_login.user_logged_in.connect(stamp_session)
    flask_login.user_logged_out.connect(discard_session)


def get_session_manager() -> type[_common.AbstractSessionManager]:
    origin = _common.get_origin()
    match origin:
        case _common.Origin.PRO:
            return _pro.SessionManager
        case _common.Origin.NATIVE:
            return _native.SessionManager
        case _:
            raise _common.ForbiddenOrigin("you should come either from pro or native")


def request_loader(request: flask.Request) -> users_models.User | None:
    return get_session_manager().request_loader(request=request)


def stamp_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
    return get_session_manager().stamp_session(app=app, user=user)


def discard_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
    return get_session_manager().discard_session(app=app, user=user)
