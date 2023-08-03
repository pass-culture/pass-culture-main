import logging

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
