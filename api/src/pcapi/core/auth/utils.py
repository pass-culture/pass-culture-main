import typing

from flask import g

from pcapi.core.users import models as users_models
from pcapi.flask_app import app


CURRENT_USER_GLOBAL_NAME = "current_account"
CURRENT_PERMISSIONS_GLOBAL_NAME = "current_permissions"


def __get_global(name: str, default: typing.Any) -> typing.Any:
    return getattr(g, name, default)


def __set_global(name: str, value: typing.Any) -> None:
    return setattr(g, name, value)


def __teardown_global(name: str) -> None:
    g.pop(name, None)


def get_current_user() -> users_models.User:
    return __get_global(CURRENT_USER_GLOBAL_NAME, None)


def _set_current_user(user: users_models.User) -> None:
    __set_global(CURRENT_USER_GLOBAL_NAME, user)


@app.teardown_appcontext
def teardown_current_user(_exception: BaseException | None = None) -> None:
    __teardown_global(CURRENT_USER_GLOBAL_NAME)


def get_current_permissions() -> typing.Iterable[str]:
    return __get_global(CURRENT_PERMISSIONS_GLOBAL_NAME, [])


def _set_current_permissions(permissions: typing.Iterable[str]) -> None:
    __set_global(CURRENT_PERMISSIONS_GLOBAL_NAME, permissions)


@app.teardown_appcontext
def teardown_current_permissions(_exception: BaseException | None = None) -> None:
    __teardown_global(CURRENT_PERMISSIONS_GLOBAL_NAME)
