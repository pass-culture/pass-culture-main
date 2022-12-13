import logging

from pcapi.core.mails.transactional.users.ubble.ubble_ko_reminder import send_reminder_emails
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("send_beneficiary_subscription_reminders")
@log_cron_with_transaction
def send_beneficiary_subscription_reminders() -> None:
    send_reminder_emails()
