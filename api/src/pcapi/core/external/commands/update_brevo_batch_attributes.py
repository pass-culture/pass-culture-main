"""
Fetch users from database and update their information in Batch and Brevo.
Goal: some users do not have all the expected attributes, this script should
fix this issue.
"""

from dataclasses import dataclass
import logging
import time

import sqlalchemy as sa
import urllib3.exceptions

from pcapi.core.external import batch
from pcapi.core.external import sendinblue
from pcapi.core.external.attributes.api import get_user_attributes
from pcapi.core.external.attributes.models import UserAttributes
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.notifications.push import update_users_attributes
from pcapi.notifications.push.backends.batch import UserUpdateData


logger = logging.getLogger(__name__)


@dataclass
class CollectedAttributes:
    email: str
    attributes: UserAttributes


def _collect_users_attributes(users: list[User]) -> list[CollectedAttributes]:
    # Collect once for both Brevo and Batch
    results: list[CollectedAttributes] = []
    for user in users:
        try:
            attributes = get_user_attributes(user)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # This user will not be updated, do not make the whole command crash, trace the exception
            logger.exception(
                "[update_brevo_and_batch_users] Failed to collect user attributes: %s",
                str(exc),
                extra={"user_id": user.id},
            )
        else:
            results.append(CollectedAttributes(email=user.email, attributes=attributes))

    return results


def _format_batch_users(users_attributes: list[CollectedAttributes]) -> list[UserUpdateData]:
    res = []
    for user_attributes in users_attributes:
        attributes = batch.format_user_attributes(user_attributes.attributes)
        res.append(UserUpdateData(user_id=str(user_attributes.attributes.user_id), attributes=attributes))
    logger.info("[update_brevo_and_batch_users] %d users formatted for Batch...", len(res))
    return res


def _format_brevo_users(users_attributes: list[CollectedAttributes]) -> list[sendinblue.SendinblueUserUpdateData]:
    res = []
    for user_attributes in users_attributes:
        attributes = sendinblue.format_user_attributes(user_attributes.attributes)
        res.append(sendinblue.SendinblueUserUpdateData(email=user_attributes.email, attributes=attributes))
    logger.info("[update_brevo_and_batch_users] %d users formatted for Brevo...", len(res))
    return res


def _run_iteration(min_user_id: int, max_user_id: int, synchronize_batch: bool, synchronize_brevo: bool) -> None:
    message = (
        "Update multiple user attributes in "
        f"[{'Batch, ' if synchronize_batch else ''}{'Brevo' if synchronize_brevo else ''}] "
        f"with user ids in range {min_user_id}-{max_user_id}"
    )

    user_ids = list(range(min_user_id, max_user_id + 1))

    logger.info("[update_brevo_and_batch_users] %s started", message)
    chunk = (
        db.session.query(User)
        .filter(User.id.in_(user_ids))
        .filter(
            User.isActive.is_(True),
            sa.or_(  # type: ignore[type-var]
                sa.and_(
                    sa.not_(User.has_pro_role),
                    sa.not_(User.has_non_attached_pro_role),
                    sa.not_(User.has_admin_role),
                ),
                User.is_beneficiary,
            ),
        )
        .all()
    )

    retries = 3
    while retries > 0:
        retries -= 1
        try:
            user_attributes = _collect_users_attributes(chunk)
            if synchronize_batch:
                batch_users_data = _format_batch_users(user_attributes)
                update_users_attributes(batch_users_data)
            if synchronize_brevo:
                brevo_users_data = _format_brevo_users(user_attributes)
                sendinblue.import_contacts_in_sendinblue(brevo_users_data)
        except (TimeoutError, urllib3.exceptions.TimeoutError) as exc:
            if retries == 0:
                raise
            logger.info("[update_brevo_and_batch_users] A timeout exception occurred: %s", exc)
            logger.info("[update_brevo_and_batch_users] Retry after 30 seconds...")
            time.sleep(30)
        else:
            break

    logger.info("[update_brevo_and_batch_users] %d users updated", len(chunk))


def update_brevo_and_batch_loop(chunk_size: int, min_id: int, max_id: int, sync_brevo: bool, sync_batch: bool) -> None:
    if not sync_brevo and not sync_batch:
        logger.info(
            "[update_brevo_and_batch_users] /!\\ /!\\ /!\\ Both Brevo and Batch skipped -> dry run /!\\ /!\\ /!\\"
        )
        logger.info("[update_brevo_and_batch_users] Use --sync-brevo and/or --sync-batch to really update")

    # Process users in the order of ids so that we can resume easily in case the script is interrupted.
    # Start from the most recent users is almost an arbitrary choice (supposed to be most active users).
    if not max_id:
        max_id = db.session.query(User).order_by(User.id.desc()).first().id

    try:
        for current_max_id in range(max_id, min_id, -chunk_size):
            current_min_id = max(current_max_id - chunk_size + 1, min_id)

            _run_iteration(current_min_id, current_max_id, sync_batch, sync_brevo)

            # Ensure that script is not killed in production environment because of memory usage.
            db.session.expunge_all()
    except KeyboardInterrupt:
        logger.info(
            "[update_brevo_and_batch_users] ===> Manually stopped, process can be resumed with --max-id=%d",
            current_max_id,
        )
    else:
        logger.info("[update_brevo_and_batch_users] Completed.")
