import logging

import pcapi.scheduled_tasks.decorators as cron_decorators
from pcapi.utils.blueprint import Blueprint

from . import api


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("archive_old_bookings")
@cron_decorators.log_cron_with_transaction
def archive_old_bookings() -> None:
    api.archive_old_bookings()
