"""
Fetch users from database and update their informations on Batch.
Goal: some users do not have all the expected attributes, this script should
fix this issue.
"""
from itertools import islice
import logging
from typing import Generator

from pcapi.core.users.external import get_user_bookings
from pcapi.core.users.external.batch import get_user_attributes
from pcapi.models import User
from pcapi.notifications.push import update_users_attributes
from pcapi.notifications.push.backends.batch import UserUpdateData


logger = logging.getLogger(__name__)


def get_users(batch_size: int) -> Generator[User, None, None]:
    """Fetch users from database, without loading all of them at once."""
    try:
        for user in User.query.yield_per(batch_size):
            yield user
    except Exception as err:
        print("Users fetch failed: %s", err)
        raise
    else:
        print("All users fetched")


def get_users_chunks(chunk_size: int) -> Generator[list[User], None, None]:
    users = get_users(chunk_size)
    while True:
        chunk = list(islice(users, chunk_size))
        if chunk:
            yield chunk

        if len(chunk) < chunk_size:
            break


def format_users(users: list[User]) -> list[UserUpdateData]:
    res = []
    for user in users:
        user_bookings = get_user_bookings(user)
        attributes = get_user_attributes(user, user_bookings)

        res.append(UserUpdateData(user_id=str(user.id), attributes=attributes))
    print(f"{len(res)} users formatted...")
    return res


def run(chunk_size: int) -> None:
    logger.info("Update multiple user attributes in Batch started")
    for chunk in get_users_chunks(chunk_size):
        users_data = format_users(chunk)
        update_users_attributes(users_data)
    logger.info("Update multiple user attributes in Batch finished")
