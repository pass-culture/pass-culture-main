import typing

from flask import current_app


if typing.TYPE_CHECKING:
    from redis import Redis


def get_redis_client() -> "Redis[str]":
    # set in flask_app
    return current_app.redis_client
