import datetime
import logging

import click
import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import synchronize_venues_banners_with_google_places as banner_url_synchronizations
from pcapi.core.offerers import tasks as offerers_tasks
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("check_active_offerers")
@click.option("--dry-run", type=bool, default=False)
def check_active_offerers(dry_run: bool = False) -> None:
    # This command is called from a cron running every day, so that any active offerer is checked every month.
    # Split into 28 blocks to avoid spamming Sirene API for all offerers the same day. Nothing done on 29, 30, 31.

    siren_caduc_tag_id_subquery = (
        db.session.query(offerers_models.OffererTag.id)
        .filter(offerers_models.OffererTag.name == "siren-caduc")
        .limit(1)
        .scalar_subquery()
    )

    offerers = (
        offerers_models.Offerer.query.outerjoin(
            offerers_models.OffererTagMapping,
            sa.and_(
                offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id,
                offerers_models.OffererTagMapping.tagId == siren_caduc_tag_id_subquery,
            ),
        )
        .filter(
            offerers_models.Offerer.id % 28 == datetime.date.today().day - 1,
            offerers_models.Offerer.isActive,
            offerers_models.Offerer.siren.is_not(None),
            offerers_models.OffererTagMapping.id.is_(None),
        )
        .options(sa.orm.load_only(offerers_models.Offerer.siren))
        .all()
    )

    logger.info("check_offerers_alive will check %s offerers in cloud tasks today", len(offerers))

    for offerer in offerers:
        # Do not flood Sirene API (max. 30 per minute for the whole product)
        offerers_tasks.check_offerer_siren_task.delay(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, tag_when_inactive=not dry_run)
        )


@blueprint.cli.command("synchronize_venues_banners_with_google_places")
@click.argument("start_venue_id", type=int, required=False, default=0)
@click.argument("end_venue_id", type=int, required=False, default=None)
@click.argument("limit", type=int, required=False, default=None)
def synchronize_venues_banners_with_google_places(
    start_venue_id: int = 0, end_venue_id: int | None = None, limit: int | None = None
) -> None:
    """Synchronize venues banners with Google Places API.
    The command searches for venues without banner and with a permanent venue type in google places api.
    it creates entries in the database for the venues with the banner url found in google places api and stores their placeId.
    then it aploads the banner to gcp and stores the url in the database.
    """
    banner_url_synchronizations.delete_venues_banners(start_venue_id, end_venue_id, limit)
    banner_url_synchronizations.synchronize_venues_banners_with_google_places(start_venue_id, end_venue_id, limit)
