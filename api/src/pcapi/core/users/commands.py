import logging

from pcapi import settings
import pcapi.core.fraud.api as fraud_api
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
