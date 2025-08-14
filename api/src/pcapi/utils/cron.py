import logging
import time
import typing
from enum import Enum
from functools import wraps

from pcapi.models import db
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


class CronStatus(Enum):
    STARTED = "started"
    ENDED = "ended"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value


def build_cron_log_message(name: str, status: CronStatus | None, duration: int | float | None = None) -> str:
    log_message = f"type=cron name={name} status={status}"

    if duration:
        log_message += f" duration={duration}"

    return log_message


def cron_require_feature(feature_toggle: FeatureToggle) -> typing.Callable:
    def decorator(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            if feature_toggle.is_active():
                return func(*args, **kwargs)
            logger.info("%s is not active", feature_toggle)
            return None

        return wrapper

    return decorator


def log_cron_with_transaction(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        start_time = time.time()
        logger.info(build_cron_log_message(name=func.__name__, status=CronStatus.STARTED))

        status = None  # avoid "used-before-assignment" linter warning in `finally`
        try:
            result = func(*args, **kwargs)
            # Check if there is something to commit. This avoids idle-in-transaction timeout exception in cron tasks
            # which takes long time and do not write anything in database (e.g. sendinblue automation tasks only read
            # database and often take more than one hour in production).
            if db.session.dirty:
                db.session.commit()
            status = CronStatus.ENDED
        except Exception as exception:
            if db.session.dirty:
                db.session.rollback()
            status = CronStatus.FAILED
            raise exception
        finally:
            duration = time.time() - start_time
            logger.info(build_cron_log_message(name=func.__name__, status=status, duration=duration))

        return result

    return wrapper


def log_cron(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        start_time = time.time()
        logger.info(build_cron_log_message(name=func.__name__, status=CronStatus.STARTED))

        status = None  # avoid "used-before-assignment" linter warning in `finally`
        try:
            result = func(*args, **kwargs)
            status = CronStatus.ENDED
        except Exception as exception:
            status = CronStatus.FAILED
            raise exception
        finally:
            duration = time.time() - start_time
            logger.info(build_cron_log_message(name=func.__name__, status=status, duration=duration))
        return result

    return wrapper
