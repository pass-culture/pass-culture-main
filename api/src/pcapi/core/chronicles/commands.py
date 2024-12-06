import logging

from pcapi.scheduled_tasks import decorators as cron_decorators
from pcapi.utils.blueprint import Blueprint

from . import api


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("import_book_club_chronicle")
@cron_decorators.log_cron
def import_book_club_chronicle() -> None:
    api.import_book_club_chronicles()
