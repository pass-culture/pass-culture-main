import logging
from typing import Any

import click

from pcapi import settings
from pcapi.core.mails.transactional.users import online_event_reminder
from pcapi.core.subscription.api import get_user_subscription_state
import pcapi.core.users.api as user_api
import pcapi.core.users.constants as users_constants
from pcapi.core.users.models import User
from pcapi.core.users.young_status import YoungStatus
import pcapi.scheduled_tasks.decorators as cron_decorators
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("notify_users_before_deletion_of_suspended_account")
@cron_decorators.log_cron_with_transaction
def notify_users_before_deletion_of_suspended_account() -> None:
    user_api.notify_users_before_deletion_of_suspended_account()


@blueprint.cli.command("notify_users_before_online_event")
@cron_decorators.log_cron_with_transaction
def notify_users_before_online_event() -> None:
    online_event_reminder.send_online_event_event_reminder()


@blueprint.cli.command("delete_suspended_accounts_after_withdrawal_period")
@cron_decorators.log_cron_with_transaction
def delete_suspended_accounts_after_withdrawal_period() -> None:
    query = user_api.get_suspended_upon_user_request_accounts_since(settings.DELETE_SUSPENDED_ACCOUNTS_SINCE)
    for user in query:
        user_api.suspend_account(user, users_constants.SuspensionReason.DELETED, None)


@blueprint.cli.command("anonymize_inactive_users")
@click.option(
    "--category",
    type=click.Choice(("pro", "beneficiary", "neither", "all"), case_sensitive=False),
    help="""Choose which users to anonymize:
    pro: anonymize pro users afer X years [not implemented]
    beneficiary: anonymize beneficiary users 3 years after their last connection, starting from the 5 years after the expiration of their deposits; also anonymize deposits 10 years after their expiration
    neither: anonymize users that have never been pro or beneficiaries 3 years after their last connection
    all: anonymize all the users respecting their time rules
    """,
    required=True,
)
@click.option(
    "--force",
    type=bool,
    help="If True users will be anonymized even if they have an address without an IRIS",
    is_flag=True,
    default=False,
)
@cron_decorators.log_cron_with_transaction
def anonymize_inactive_users(category: str, force: bool) -> None:
    if category in ("beneficiary", "all"):
        print("Anonymize beneficiary users after 5 years")
        user_api.anonymize_beneficiary_users(force=force)
        user_api.anonymize_user_deposits()
    if category in ("neither", "all"):
        print("Anonymizing users that are neither beneficiaries nor pro 3 years after their last connection")
        user_api.anonymize_non_pro_non_beneficiary_users(force=force)
    if category in ("pro", "all"):
        print("Anonymizing pro users X years after their last connection [not implemented]")


# TODO (2024-02-19, cepehang) delete after usage
@blueprint.cli.command("get_unknown_status_by_user_id")
@click.option(
    "--from-id",
    type=int,
    help="User id from which to check for unknown young status",
    default=0,
)
def get_unknown_status_by_user_id(from_id: int) -> None:
    last_id = from_id
    unknown_status_by_user_id: dict[int, Any] = {}
    while True:
        users = User.query.filter(User.id > last_id).order_by(User.id).limit(1000).all()
        if not users:
            break

        for user in users:
            try:
                young_status = get_user_subscription_state(user).young_status
                if not isinstance(young_status, YoungStatus):
                    unknown_status_by_user_id[user.id] = young_status
            except Exception:  # pylint: disable=broad-exception-caught
                unknown_status_by_user_id[user.id] = young_status

        last_id = users[-1].id
        logger.info("last checked user id: %s", last_id)

    if unknown_status_by_user_id:
        logger.warning(unknown_status_by_user_id)
    else:
        logger.info("all good, no unknown young status was found")
