import logging

from pcapi.core.highlights import repository as highlights_repository
from pcapi.core.mails import transactional as transactional_mails
from pcapi.utils import cron as cron_decorators
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)

blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("send_email_highlight_communication")
@cron_decorators.log_cron_with_transaction
def send_email_highlight_communication() -> None:
    """Triggers email to be sent for highlights with communication_date to today"""
    requests_for_today_highlights = highlights_repository.get_today_highlight_requests()
    for highlight_request in requests_for_today_highlights:
        transactional_mails.send_highlight_communication_email_to_pro(highlight_request.offer)
