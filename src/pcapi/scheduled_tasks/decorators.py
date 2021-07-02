from functools import wraps
import logging
import time

from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.logger import CronStatus
from pcapi.scheduled_tasks.logger import build_cron_log_message


logger = logging.getLogger(__name__)


def cron_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        clock_application = args[0]
        with clock_application.app_context():
            return func(*args, **kwargs)

    return wrapper


def cron_require_feature(feature_toggle: FeatureToggle):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if feature_toggle.is_active():
                return func(*args, **kwargs)
            logger.info("%s is not active", feature_toggle)
            return None

        return wrapper

    return decorator


def log_cron(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(build_cron_log_message(name=func.__name__, status=CronStatus.STARTED))

        result = func(*args, **kwargs)

        end_time = time.time()
        duration = end_time - start_time
        logger.info(build_cron_log_message(name=func.__name__, status=CronStatus.ENDED, duration=duration))
        return result

    return wrapper
