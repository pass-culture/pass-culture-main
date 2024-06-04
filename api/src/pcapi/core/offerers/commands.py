import datetime
import logging
from math import ceil

import click
import sqlalchemy as sa

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import synchronize_venues_banners_with_google_places as banner_url_synchronizations
from pcapi.core.offerers import tasks as offerers_tasks
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


@blueprint.cli.command("check_active_offerers")
@click.option("--dry-run", type=bool, default=False)
@click.option("--day", type=int, required=False, default=None)
def check_active_offerers(dry_run: bool = False, day: int | None = None) -> None:
    # This command is called from a cron running every day, so that any active offerer is checked every month.
    # Split into 28 blocks to avoid spamming Sirene API for all offerers the same day. Nothing done on 29, 30, 31.
    # Use --day to replay or troubleshooting.

    if day is None:
        day = datetime.date.today().day

    siren_caduc_tag_id_subquery = (
        db.session.query(offerers_models.OffererTag.id)
        .filter(offerers_models.OffererTag.name == "siren-caduc")
        .limit(1)
        .scalar_subquery()
    )

    offerers_query = offerers_models.Offerer.query.filter(
        offerers_models.Offerer.id % 28 == day - 1,
        offerers_models.Offerer.isActive,
        sa.not_(offerers_models.Offerer.isRejected),
        offerers_models.Offerer.siren.is_not(None),
    ).options(sa.orm.load_only(offerers_models.Offerer.siren))

    if not FeatureToggle.ENABLE_CODIR_OFFERERS_REPORT.is_active():
        # When FF is disabled, we only have to check if siren-caduc tag has to be applied, skip already tagged
        offerers_query = offerers_query.outerjoin(
            offerers_models.OffererTagMapping,
            sa.and_(
                offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id,
                offerers_models.OffererTagMapping.tagId == siren_caduc_tag_id_subquery,
            ),
        ).filter(offerers_models.OffererTagMapping.id.is_(None))

    offerers = offerers_query.all()

    logger.info("check_offerers_alive will check %s offerers in cloud tasks today", len(offerers))

    for offerer in offerers:
        # Do not flood Sirene API (max. 30 per minute for the whole product)
        offerers_tasks.check_offerer_siren_task.delay(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, tag_when_inactive=not dry_run)
        )


@blueprint.cli.command("synchronize_venues_banners_with_google_places")
@click.option("--frequency", type=int, required=False, default=1)
def synchronize_venues_banners_with_google_places(frequency: int = 1) -> None:
    """Synchronize venues banners with Google Places API.

    This command is meant to be called every day.
    The `frequency` parameter is used to split the venues into blocks, to update a fraction of the venues every day.
    1 means all venues are updated once a month, 2 means twice a month, 4 means once a week.

    Args:
        frequency (int): The frequency of the command per month. Default is 1, to synchronize all venues once a month.
    """

    if frequency not in (1, 2, 4):
        raise click.BadParameter("frequency must be 1, 2 or 4")

    day = datetime.date.today().day
    if day > banner_url_synchronizations.SHORTEST_MONTH_LENGTH:
        logger.info(
            "[gmaps_banner_synchro] synchronize_venues_banners_with_google_places command does not execute after 28th"
        )
        return

    venues = banner_url_synchronizations.get_venues_without_photo(frequency)
    banner_url_synchronizations.delete_venues_banners(venues)
    banner_url_synchronizations.synchronize_venues_banners_with_google_places(venues)


@blueprint.cli.command("synchronize_accessibility_with_acceslibre")
@click.option("--dry-run", type=bool, default=False)
@click.option("--force-sync", type=bool, default=False)
@click.option("--start-from-batch", type=int, default=1, help="Start synchronization from batch number")
def synchronize_accessibility_with_acceslibre(
    dry_run: bool = False, force_sync: bool = False, start_from_batch: int = 1
) -> None:
    """
    For all venues synchronized with acceslibre, we fetch on a weekly basis the
    last_update_at and update their accessibility information.

    If we use the --force_sync flag, it will not check for last_update_at

    If we use the --start-from-batch option, it will start synchronization from the given batch number
    Use case: synchronization has failed with message "Could not update batch <n>"

    If externalAccessibilityId can't be found at acceslibre, we try to find a new match, cf. synchronize_accessibility_provider()
    """
    venues_count = offerers_api.count_permanent_venues_with_accessibility_provider()
    num_batches = ceil(venues_count / BATCH_SIZE)
    if start_from_batch > num_batches:
        click.echo(f"Start from batch must be less than {num_batches}")
        return

    start_batch_index = start_from_batch - 1
    for i in range(start_batch_index, num_batches):
        venues_list = offerers_api.get_permanent_venues_with_accessibility_provider(batch_size=BATCH_SIZE, batch_num=i)
        for venue in venues_list:
            offerers_api.synchronize_accessibility_provider(venue, force_sync)

        if not dry_run:
            try:
                db.session.commit()
            except sa.exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i + 1)
                db.session.rollback()
        else:
            db.session.rollback()


@blueprint.cli.command("synchronize_venues_with_acceslibre")
@click.argument("venue_ids", type=int, nargs=-1, required=True)
@click.option("--dry-run", type=bool, default=True)
def synchronize_venues_with_acceslibre(venue_ids: list[int], dry_run: bool = True) -> None:
    offerers_api.synchronize_venues_with_acceslibre(venue_ids, dry_run)


@blueprint.cli.command("acceslibre_matching")
@click.option("--dry-run", type=bool, default=False)
@click.option("--batch-size", type=int, default=BATCH_SIZE, help="Size of venues batches to synchronize")
@click.option("--start-from-batch", type=int, default=1, help="Start synchronization from batch number")
@click.option("--n-days-to-fetch", type=int, default=7, help="Number of days to look for new data at acceslibre")
def acceslibre_matching(
    dry_run: bool = False, batch_size: int = BATCH_SIZE, start_from_batch: int = 1, n_days_to_fetch: int = 7
) -> None:
    offerers_api.acceslibre_matching(
        batch_size=batch_size, dry_run=dry_run, start_from_batch=start_from_batch, n_days_to_fetch=n_days_to_fetch
    )
