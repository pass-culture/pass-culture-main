import logging
import time
import typing
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps

from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


# helper to serialize pro user's
def get_pro_user_helper(user: users_models.User) -> dict:
    return {"email": user.email}


@dataclass
class StepsSelect:
    steps_to_skip: list[str]
    steps_to_run: list[str]


STEPS_SELECT = StepsSelect(steps_to_skip=[], steps_to_run=[])


@contextmanager
def select_steps(
    steps_to_skip: typing.Sequence[str] | None, steps_to_run: typing.Sequence[str] | None
) -> typing.Iterator[None]:
    """
    This context manager allows to select / skip calls of functions decorated with log_func_duration

    Example skip:

    @log_func_duration
    def my_step():
        ...

    def sandbox():
        ...
        my_step()
        ...

    with select_steps(steps_to_skip=["my_step"]):
        sandbox() # my_step will not be called here

    Example select:

    @log_func_duration
    def my_step_1():
        ...

    @log_func_duration
    def my_step_2():
        ...

    def sandbox():
        ...
        my_step_1()
        my_step_2()
        ...

    with select_steps(steps_to_run=["my_step_1"]):
        sandbox() # my_step_2 will not be called here
    """
    if steps_to_skip and steps_to_run:
        raise ValueError("Only one of steps_to_skip or steps_to_run should be provided")

    try:
        if steps_to_skip:
            STEPS_SELECT.steps_to_skip = list(steps_to_skip)
        if steps_to_run:
            STEPS_SELECT.steps_to_run = list(steps_to_run)
        yield

    finally:
        STEPS_SELECT.steps_to_skip = []
        STEPS_SELECT.steps_to_run = []


def log_func_duration(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if STEPS_SELECT.steps_to_skip and func.__name__ in STEPS_SELECT.steps_to_skip:
            logger.info("Skipped %s", func.__name__)
            return

        if STEPS_SELECT.steps_to_run and func.__name__ not in STEPS_SELECT.steps_to_run:
            logger.info("Skipped %s", func.__name__)
            return

        start_time = time.time()
        result = func(*args, **kwargs)
        logger.info("Executed %s in %.2fs", func.__name__, time.time() - start_time)

        return result

    return wrapper
