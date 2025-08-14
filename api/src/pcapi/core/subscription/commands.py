import logging

import pcapi.utils.cron as cron_decorators
from pcapi.core.mails.transactional.users.ubble import reminder_emails
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("send_beneficiary_subscription_reminders")
@cron_decorators.log_cron_with_transaction
def send_beneficiary_subscription_reminders() -> None:
    reminder_emails.send_reminders()
