from pcapi.core.mails.transactional.users import online_event_reminder
import pcapi.scheduled_tasks.decorators as cron_decorators
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("send_online_event_reminders")
@cron_decorators.log_cron_with_transaction
def send_online_event_reminders() -> None:
    online_event_reminder.send_online_event_event_reminder_by_offer()
