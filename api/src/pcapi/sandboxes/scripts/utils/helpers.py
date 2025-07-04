import logging
import time
import typing
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


def log_func_duration(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        logger.info("Executed %s in %.2fs", func.__name__, time.time() - start_time)

        return result

    return wrapper
