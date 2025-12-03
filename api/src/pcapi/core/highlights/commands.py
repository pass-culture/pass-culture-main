import logging

from pcapi.core.highlights import api as highlights_api
from pcapi.utils import cron as cron_decorators
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)

blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("send_email_highlight_communication")
@cron_decorators.log_cron
def send_email_highlight_communication() -> None:
    """Triggers email to be sent for highlights with communication_date to today"""
    highlights_api.send_email_for_highlight_with_communication_date_set_to_today()
