import pcapi.core.offers.api as offers_api
from pcapi.core.reminders.external import reminders_notifications
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("activate_future_offers")
@log_cron_with_transaction
def activate_future_offers() -> None:
    offers_api.activate_future_offers()
    reminders_notifications.notify_users_for_future_offers_activations()


@blueprint.cli.command("set_upper_timespan_of_inactive_headline_offers")
@log_cron_with_transaction
def set_upper_timespan_of_inactive_headline_offers() -> None:
    offers_api.set_upper_timespan_of_inactive_headline_offers()
