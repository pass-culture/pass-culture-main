import logging

import click

from pcapi.models import db
import pcapi.scheduled_tasks.decorators as cron_decorators
from pcapi.utils.blueprint import Blueprint

from . import api


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("archive_old_bookings")
@cron_decorators.log_cron_with_transaction
def archive_old_bookings() -> None:
    api.archive_old_bookings()


@blueprint.cli.command("recompute_dnBookedQuantity")
@click.argument("stock-ids", type=int, nargs=-1, required=True)
@click.option("--dry-run", type=bool, default=True)
def recompute_dnBookedQuantity(stock_ids: list[int], dry_run: bool = True) -> None:
    api.recompute_dnBookedQuantity(stock_ids)
    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()
