from functools import wraps

from pcapi.flask_app import app
from pcapi.settings import IS_RUNNING_TESTS
from pcapi.utils.logger import logger
from pcapi.workers.logger import JobStatus
from pcapi.workers.logger import build_job_log_message


def job_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # TODO(xordoquy): use flask.current_app to retrieve context
        if IS_RUNNING_TESTS:
            # in TESTS, queued jobs are executed synchronously and we don't won't to create another session
            return func(*args, **kwargs)

        with app.app_context():
            return func(*args, **kwargs)

    return wrapper


def log_job(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        job_description = f"{func.__name__} {args}"
        logger.info(build_job_log_message(job=job_description, status=JobStatus.STARTED))
        result = func(*args, **kwargs)

        logger.info(build_job_log_message(job=job_description, status=JobStatus.ENDED))
        return result

    return wrapper
