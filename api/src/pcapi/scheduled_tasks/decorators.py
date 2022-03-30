from functools import wraps
import logging
import time

from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.logger import CronStatus
from pcapi.scheduled_tasks.logger import build_cron_log_message


logger = logging.getLogger(__name__)


def cron_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # The `flask clock` command sets up an application context,
        # but it gets lost when apscheduler starts a job in a new
        # thread. So here we must set an application context again.
        from pcapi.flask_app import app

        with app.app_context():
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


def log_cron_with_transaction(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(build_cron_log_message(name=func.__name__, status=CronStatus.STARTED))

        status = None  # avoid "used-before-assignment" pylint warning in `finally`
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            status = CronStatus.ENDED
        except Exception as exception:
            db.session.rollback()
            status = CronStatus.FAILED
            raise exception
        finally:
            duration = time.time() - start_time
            logger.info(build_cron_log_message(name=func.__name__, status=status, duration=duration))

        return result

    return wrapper
