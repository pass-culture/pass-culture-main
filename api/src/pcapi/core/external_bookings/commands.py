import logging

from pcapi.utils.blueprint import Blueprint

from . import api


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("disable_external_bookings")
def disable_external_bookings() -> None:
    api.disable_external_bookings()
