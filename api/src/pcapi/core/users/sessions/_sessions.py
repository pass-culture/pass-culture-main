import typing

from flask.sessions import SecureCookieSessionInterface
from flask.sessions import SessionMixin
from werkzeug.datastructures import CallbackDict

from . import _common


NATIVE_SESSION_KEYS = {
    "_user_id",
    "_fresh",
    "_id",
}


class SessionUnavailableException(Exception):
    pass


class CustomSession(CallbackDict[str, typing.Any], SessionMixin):
    """
    Custom session to crash if we try to write in it on a native route.
    Three keys are whitelisted to permet the usage of 'login_user' in refresh route.
    """

    modified = False
    _is_native: bool | None = None

    def __init__(self, initial: typing.Any | None = None) -> None:
        def on_update(self: typing.Self) -> None:
            self.modified = True
            if self._is_native is None:
                self._is_native = _common.get_origin() == _common.Origin.NATIVE
            if self._is_native:
                for key in self.keys():
                    if key not in NATIVE_SESSION_KEYS:
                        raise SessionUnavailableException(key)

        super().__init__(initial, on_update)


class CustomSessionInterface(SecureCookieSessionInterface):
    session_class = CustomSession  # type: ignore [assignment]
