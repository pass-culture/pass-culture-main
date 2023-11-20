import logging

import click

from pcapi import settings
import pcapi.core.users.api as user_api
import pcapi.core.users.constants as users_constants
import pcapi.scheduled_tasks.decorators as cron_decorators
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("notify_users_before_deletion_of_suspended_account")
@cron_decorators.log_cron_with_transaction
def notify_users_before_deletion_of_suspended_account() -> None:
    user_api.notify_users_before_deletion_of_suspended_account()


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
    beneficiary: anonymize beneficiary users 5 years after their last connection or the expiration of their deposits (whichever is the later) [not implemented]
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
        print("Anonymize beneficiary users after 5 years [not implemented]")
    if category in ("neither", "all"):
        print("Anonymising users that are neither beneficiaries nor pro 3 years after their last connection")
        user_api.anonymize_non_pro_non_beneficiary_users(force=force)
    if category in ("pro", "all"):
        print("Anonymising pro users X years after their last connection [not implemented]")
