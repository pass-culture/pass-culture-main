"""
Fetch users from database and update their information in Batch and Sendinblue.
Goal: some users do not have all the expected attributes, this script should
fix this issue.
"""
import sys

from pcapi.core.users.external import batch
from pcapi.core.users.external import get_user_attributes
from pcapi.core.users.external import get_user_or_pro_attributes
from pcapi.core.users.external import sendinblue
from pcapi.core.users.external.sendinblue import SendinblueUserUpdateData
from pcapi.core.users.external.sendinblue import import_contacts_in_sendinblue
from pcapi.core.users.models import User
from pcapi.notifications.push import update_users_attributes
from pcapi.notifications.push.backends.batch import UserUpdateData


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
        attributes = sendinblue.format_user_attributes(get_user_or_pro_attributes(user))
        res.append(SendinblueUserUpdateData(email=user.email, attributes=attributes))  # type: ignore [arg-type]
    print(f"{len(res)} users formatted for sendinblue...")
    return res


def run(
    min_user_id: int, max_user_id: int, synchronize_batch: bool = True, synchronize_sendinblue: bool = True
) -> None:
    if not synchronize_batch and not synchronize_sendinblue:
        print("No user synchronized, please set synchronize_batch or synchronize_sendinblue to True")
        return

    message = (
        "Update multiple user attributes in "
        f"[{'Batch, ' if synchronize_batch else ''}{'Sendinblue' if synchronize_sendinblue else ''}] "
        f"with user ids in range {min_user_id}-{max_user_id}"
    )

    user_ids = list(range(min_user_id, max_user_id + 1))

    print("%s started" % message)
    chunk = (
        User.query.filter(User.id.in_(user_ids))
        .filter(User.has_pro_role.is_(False))  # type: ignore [attr-defined]
        .filter(User.has_admin_role.is_(False))  # type: ignore [attr-defined]
        .all()
    )
    if synchronize_batch:
        batch_users_data = format_batch_users(chunk)
        update_users_attributes(batch_users_data)
    if synchronize_sendinblue:
        sendinblue_users_data = format_sendinblue_users(chunk)
        import_contacts_in_sendinblue(sendinblue_users_data)

    print("%s users updated" % len(chunk))


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    if len(sys.argv) != 3:
        raise ValueError("This script requires two arguments: min and max ids")
    user_id_bounds = [int(v) for v in sys.argv[1:3]]

    arg_min_user_id = min(user_id_bounds)
    arg_max_user_id = max(user_id_bounds)

    run(arg_min_user_id, arg_max_user_id, synchronize_batch=True, synchronize_sendinblue=True)
