"""
Fetch users without the PRO role and with a not validated `UserOfferer` on Batch.
"""

from itertools import islice
from typing import Generator

import sqlalchemy as sa

from pcapi.core.offerers.models import UserOfferer
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus


def get_users(batch_size: int) -> Generator[User, None, None]:
    """Fetch users from database, without loading all of them at once."""
    try:
        yield from (
            User.query.join(UserOfferer)
            .filter(
                sa.not_(User.roles.any(UserRole.PRO)),
                sa.not_(User.roles.any(UserRole.NON_ATTACHED_PRO)),
                UserOfferer.validationStatus != ValidationStatus.VALIDATED,
            )
            .yield_per(batch_size)
        )
    except Exception as err:
        print(f"Users fetch failed: {err}")
        raise
    print("All users fetched")


def get_users_chunks(chunk_size: int) -> Generator[list[User], None, None]:
    users = get_users(chunk_size)
    while True:
        chunk = list(islice(users, chunk_size))
        if chunk:
            yield chunk

        if len(chunk) < chunk_size:
            break


def run(dry_run: bool = True, chunk_size: int = 1000) -> None:
    message = "user non attached pro role migration"
    print(f"Starting {message} ...")
    for chunk in get_users_chunks(chunk_size):
        for user in chunk:
            user.add_non_attached_pro_role()
        print(f"Updated users {[user.id for user in chunk]}")
    if dry_run:
        db.session.rollback()
        print("Did rollback. Use dry_run = False if you want the script to commit.")
    else:
        db.session.commit()
        print("Did commit changes.")

    print(f"... {message} finished")
