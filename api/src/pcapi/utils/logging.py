import logging
from collections.abc import Generator
from contextlib import contextmanager


@contextmanager
def logging_at_level(target_logger: logging.Logger, level: int) -> Generator[None, None, None]:
    """
    Generator to set logging level of given logger to target level (most often to `DEBUG`) during the execution of a function
    and restore logging level to previous level afterwards.
    """
    old_level = target_logger.level
    target_logger.setLevel(level)

    try:
        yield
    finally:
        target_logger.setLevel(old_level)
