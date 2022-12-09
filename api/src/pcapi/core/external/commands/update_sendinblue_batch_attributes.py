"""
Fetch users from database and update their information in Batch and Sendinblue.
Goal: some users do not have all the expected attributes, this script should
fix this issue.
"""
import click

from pcapi.core.external import batch
from pcapi.core.external import sendinblue
from pcapi.core.external.attributes.api import get_user_attributes
from pcapi.core.external.attributes.api import get_user_or_pro_attributes
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.notifications.push import update_users_attributes
from pcapi.notifications.push.backends.batch import UserUpdateData
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


def format_batch_users(users: list[User]) -> list[UserUpdateData]:
    res = []
    for user in users:
        attributes = batch.format_user_attributes(get_user_attributes(user))
        res.append(UserUpdateData(user_id=str(user.id), attributes=attributes))
    print(f"{len(res)} users formatted for batch...")
    return res


def format_sendinblue_users(users: list[User]) -> list[sendinblue.SendinblueUserUpdateData]:
    res = []
    for user in users:
        attributes = sendinblue.format_user_attributes(get_user_or_pro_attributes(user))
        res.append(sendinblue.SendinblueUserUpdateData(email=user.email, attributes=attributes))
    print(f"{len(res)} users formatted for sendinblue...")
    return res


def _run_iteration(min_user_id: int, max_user_id: int, synchronize_batch: bool, synchronize_sendinblue: bool) -> None:
    message = (
        "Update multiple user attributes in "
        f"[{'Batch, ' if synchronize_batch else ''}{'Sendinblue' if synchronize_sendinblue else ''}] "
        f"with user ids in range {min_user_id}-{max_user_id}"
    )

    user_ids = list(range(min_user_id, max_user_id + 1))

    print(f"{message} started")
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
        sendinblue.import_contacts_in_sendinblue(sendinblue_users_data)

    print(f"{len(chunk)} users updated")


def update_sendinblue_batch_loop(
    chunk_size: int, min_id: int, max_id: int, sync_sendinblue: bool, sync_batch: bool
) -> None:
    if not sync_sendinblue and not sync_batch:
        print("====================================================================")
        print("/!\\ /!\\ /!\\ Both Sendinblue and Batch skipped -> dry run /!\\ /!\\ /!\\")
        print("  Use --sync-sendinblue and/or --sync-sendinblue to really update")
        print("====================================================================")

    # Process users in the order of ids so that we can resume easily in case the script is interrupted.
    # Start from the most recent users is almost an arbitrary choice (supposed to be most active users).
    if not max_id:
        max_id = User.query.order_by(User.id.desc()).first().id

    try:
        for current_max_id in range(max_id, min_id, -chunk_size):
            current_min_id = max(current_max_id - chunk_size + 1, min_id)

            _run_iteration(current_min_id, current_max_id, sync_batch, sync_sendinblue)

            # Ensure that script is not killed in production environment because of memory usage.
            db.session.expunge_all()
    except KeyboardInterrupt:
        print(f"===> Manually stopped, process can be resumed with --max-id={current_max_id}")
    else:
        print("Completed.")


@blueprint.cli.command("update_sendinblue_batch")
@click.option("--chunk-size", type=int, default=500, help="number of users to update in one query")
@click.option("--min-id", type=int, default=0, help="minimum user id")
@click.option("--max-id", type=int, default=0, help="maximum user id")
@click.option("--sync-sendinblue", is_flag=True, default=False, help="synchronize Sendinblue")
@click.option("--sync-batch", is_flag=True, default=False, help="synchronize Batch")
def update_sendinblue_batch(chunk_size: int, min_id: int, max_id: int, sync_sendinblue: bool, sync_batch: bool) -> None:
    update_sendinblue_batch_loop(chunk_size, min_id, max_id, sync_sendinblue, sync_batch)
