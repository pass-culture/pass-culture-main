from functools import wraps
from logging import Logger
import typing


def retry(
    exception: type[Exception],
    exception_handler: typing.Callable | None = None,
    max_attempts: int = 1,
    logger: Logger | None = None,
) -> typing.Callable:
    """
    Retry func on a given exception n (or 1 by default) times.
    Slightly adapt from https://gitlab.com/woob/woob/-/blob/master/woob/tools/decorators.py#L25
    original from https://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/

    Args:
        exception (Exception): Which exception should be catched
        exception_handler (Callable): Handler to encapsulate whatever logic you want in case exception is catched. Optional.
        max_attempts (int): How many times do you want to call `func`. Default to 1
        logger (Logger): Log the tries, if provided
    """

    def decorator(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def func_to_retry(*args: tuple, **kwargs: dict) -> typing.Any:
            inner_max_attempts = max_attempts
            while inner_max_attempts > 1:
                try:
                    return func(*args, **kwargs)
                except exception:
                    inner_max_attempts -= 1
                    if exception_handler:
                        exception_handler(*args, **kwargs)
                    if logger:
                        logger.info(
                            "Caught exception, retrying",
                            extra={"exception": exception.__name__, "remaining_attempts": inner_max_attempts},
                        )
            return func(*args, **kwargs)

        return func_to_retry

    return decorator
