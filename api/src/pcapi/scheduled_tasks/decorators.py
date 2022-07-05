from functools import wraps
import logging
import os
import time

from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.logger import CronStatus
from pcapi.scheduled_tasks.logger import build_cron_log_message


logger = logging.getLogger(__name__)


def cron_context(func):  # type: ignore [no-untyped-def]
    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore [no-untyped-def]
        # The `flask clock` command sets up an application context,
        # but it gets lost when apscheduler starts a job in a new
        # thread. So here we must set an application context again.
        from pcapi.flask_app import app

        with app.app_context():
            return func(*args, **kwargs)

    return wrapper


def cron_require_feature(feature_toggle: FeatureToggle):  # type: ignore [no-untyped-def]
    def decorator(func):  # type: ignore [no-untyped-def]
        @wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore [no-untyped-def]
            if feature_toggle.is_active():
                return func(*args, **kwargs)
            logger.info("%s is not active", feature_toggle)
            return None

        return wrapper

    return decorator


def log_cron_with_transaction(func):  # type: ignore [no-untyped-def]
    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore [no-untyped-def]
        start_time = time.time()
        logger.info(build_cron_log_message(name=func.__name__, status=CronStatus.STARTED))

        status = None  # avoid "used-before-assignment" pylint warning in `finally`
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


def log_input_args(func):  # type: ignore [no-untyped-def]
    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore [no-untyped-def]
        try:
            # Only log if an env variable has been set manually
            # If not, the caller might not realise that secret inputs
            # might be logged.
            log_args = os.getenv("CRON_LOG_ARG", "false").lower() == "true"
        except AttributeError:
            log_args = False

        if log_args:
            logger.info("%s called with args: %s and kwargs: %s", func.__name__, str(args), str(kwargs))
        return func(*args, **kwargs)

    return wrapper
