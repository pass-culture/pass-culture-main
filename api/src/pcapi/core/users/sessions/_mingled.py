from typing import Any
from typing import Callable

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


def unmingle(function: str) -> Callable:
    origin = _common.get_origin()
    match origin:
        case _common.Origin.PRO:
            return getattr(_pro, function)
        case _common.Origin.NATIVE:
            return getattr(_native, function)
        case _:
            raise _common.ForbiddenOrigin("you should come either from pro or native")


def request_loader(request: Any) -> users_models.User | None:
    return unmingle("request_loader")(request=request)


def stamp_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
    return unmingle("stamp_session")(app=app, user=user)


def discard_session(app: flask.ctx.AppContext, user: users_models.User) -> None:
    return unmingle("discard_session")(app=app, user=user)
