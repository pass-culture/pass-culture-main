import logging

import pcapi.utils.cron as cron_decorators
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint

from . import api


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("import_book_club_chronicle")
@cron_decorators.log_cron
def import_book_club_chronicle() -> None:
    if FeatureToggle.ENABLE_CHRONICLES_SYNC.is_active():
        api.import_book_club_chronicles()


@blueprint.cli.command("import_cine_club_chronicle")
@cron_decorators.log_cron
def import_cine_club_chronicle() -> None:
    if FeatureToggle.ENABLE_CHRONICLES_SYNC.is_active():
        api.import_cine_club_chronicles()


@blueprint.cli.command("import_album_club_chronicle")
@cron_decorators.log_cron
def import_album_club_chronicle() -> None:
    if FeatureToggle.ENABLE_CHRONICLES_SYNC.is_active():
        api.import_album_club_chronicles()


@blueprint.cli.command("import_concert_club_chronicle")
@cron_decorators.log_cron
def import_concert_club_chronicle() -> None:
    if FeatureToggle.ENABLE_CHRONICLES_SYNC.is_active():
        api.import_concert_club_chronicles()
