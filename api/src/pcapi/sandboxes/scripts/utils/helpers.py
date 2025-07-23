import logging
import time
import typing
from contextlib import contextmanager
from functools import wraps

from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


def get_email(first_name: str, last_name: str, domain: str) -> str:
    return "{}.{}@{}".format(
        first_name.replace(" ", "").strip().lower(), last_name.replace(" ", "").strip().lower(), domain
    )


# helper to serialize pro user's
def get_pro_user_helper(user: users_models.User) -> dict:
    return {"email": user.email}


class StepsSkip:
    def __init__(self, steps_to_skip: list[str]) -> None:
        self.steps_to_skip = steps_to_skip


STEPS_SKIP = StepsSkip(steps_to_skip=[])


@contextmanager
def skip_steps(steps: typing.Iterable[str] | None) -> typing.Iterator[None]:
    """
    This context manager allows to skip calls of functions decorated with log_func_duration

    Example:

    @log_func_duration
    def my_step():
        ...

    def sandbox():
        ...
        my_step()
        ...

    with skip_steps(steps=["my_step"]):
        sandbox() # my_step will not be called here
    """

    try:
        if steps:
            STEPS_SKIP.steps_to_skip = list(steps)
        yield

    finally:
        STEPS_SKIP.steps_to_skip = []


def log_func_duration(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if func.__name__ in STEPS_SKIP.steps_to_skip:
            logger.info("Skipped %s", func.__name__)
            return

        start_time = time.time()
        result = func(*args, **kwargs)
        logger.info("Executed %s in %.2fs", func.__name__, time.time() - start_time)

        return result

    return wrapper
