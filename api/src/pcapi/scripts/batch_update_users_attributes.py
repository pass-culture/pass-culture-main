"""
Fetch users from database and update their informations on Batch.
Goal: some users do not have all the expected attributes, this script should
fix this issue.
"""
from itertools import islice
from typing import Generator

from pcapi.core.users.external import batch
from pcapi.core.users.external import get_user_attributes
from pcapi.core.users.external import sendinblue
from pcapi.core.users.external.sendinblue import SendinblueUserUpdateData
from pcapi.core.users.external.sendinblue import import_contacts_in_sendinblue
from pcapi.models import User
from pcapi.notifications.push import update_users_attributes
from pcapi.notifications.push.backends.batch import UserUpdateData


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


def format_batch_users(users: list[User]) -> list[UserUpdateData]:
    res = []
    for user in users:
        attributes = batch.format_user_attributes(get_user_attributes(user))
        res.append(UserUpdateData(user_id=str(user.id), attributes=attributes))
    print(f"{len(res)} users formatted for batch...")
    return res


def format_sendinblue_users(users: list[User]) -> list[SendinblueUserUpdateData]:
    res = []
    for user in users:
        attributes = sendinblue.format_user_attributes(get_user_attributes(user))
        res.append(SendinblueUserUpdateData(email=user.email, attributes=attributes))
    print(f"{len(res)} users formatted for sendinblue...")
    return res


def run(chunk_size: int, synchronize_batch: bool = True, synchronize_sendinblue: bool = True) -> None:
    if not synchronize_batch and not synchronize_sendinblue:
        print("No user synchronized, please set synchronize_batch or synchronize_sendinblue to True")
        return

    message = (
        "Update multiple user attributes in "
        f"[{'Batch, ' if synchronize_batch else ''}{'Sendinblue' if synchronize_sendinblue else ''}]"
    )

    print("%s started" % message)
    for chunk in get_users_chunks(chunk_size):
        if synchronize_batch:
            batch_users_data = format_batch_users(chunk)
            update_users_attributes(batch_users_data)
        if synchronize_sendinblue:
            sendinblue_users_data = format_sendinblue_users(chunk)
            import_contacts_in_sendinblue(sendinblue_users_data)

    print("%s finished" % message)
