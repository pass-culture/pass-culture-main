import typing
from functools import wraps

from pcapi import settings

from .errors import UnauthorizedEnvironment


def exclude_prod_environment(func: typing.Callable) -> typing.Callable:
    """Ensure a route it not executed from production environment.

    The only goal is to ensure that a critical route cannot be used
    from the production environment. It wont prevent it from being
    documented by automatic tools, to avoid this, ensure that the whole
    route or module is not imported.
    """

    @wraps(func)
    def decorated_function(*args: typing.Sequence, **kwargs: typing.Mapping) -> typing.Any:
        if settings.IS_PROD:
            raise UnauthorizedEnvironment()
        return func(*args, **kwargs)

    return decorated_function
