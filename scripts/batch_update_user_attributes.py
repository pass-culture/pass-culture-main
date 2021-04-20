"""
Fetch users from database and update their informations on Batch.
Goal: some users do not have all the expected attributes, this script should
fix this issue.
"""
import logging
from typing import Generator

from pcapi.models import User
from pcapi.notifications.push.user_attributes_updates import UserUpdateData
from pcapi.notifications.push.user_attributes_updates import get_user_attributes
from pcapi.notifications.push import update_users_attributes


logger = logging.getLogger(__name__)


def get_users() -> Generator[list[User]]:
    try:
        for idx, users in enumerate(User.query.paritions(2000)):
            logger.info("partition %d fetched, %d users retrieved...", idx, len(users))
            yield users
    except Exception as err:
        logger.info("partition %d fetched, error: %s", idx, err)
        raise


def format_users(users: list[User]) -> list[UserUpdateData]:
    res = []
    for user in users:
        attributes = get_user_attributes(user)
        res.append(UserUpdateData(user_id=user.id, data=attributes))
    logger.info("%d users formatted...", len(res))
    return res


def run():
    for users in get_users():
        users_data = format_users(users)
        update_users_attributes(users_data)
    logger.info("Batch update done.")


if __name__ == '__main__':
    run()
