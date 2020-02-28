import time
from functools import wraps

from models.feature import FeatureToggle
from repository import feature_queries
from scheduled_tasks.logger import build_cron_log_message, CronStatus
from utils.logger import logger


def cron_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        clock_application = args[0]
        with clock_application.app_context() as app:
            return func(*args, **kwargs)

    return wrapper


def cron_require_feature(feature_toggle: FeatureToggle):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if feature_queries.is_active(feature_toggle):
                return func(*args, **kwargs)
            logger.info(f"{feature_toggle} is not active")

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
