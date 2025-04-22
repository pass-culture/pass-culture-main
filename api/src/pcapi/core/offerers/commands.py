import datetime
import logging

import click
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.connectors.entreprise import exceptions as entreprise_exceptions
from pcapi.connectors.entreprise import sirene
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import synchronize_venues_banners_with_google_places as banner_url_synchronizations
from pcapi.core.offerers import tasks as offerers_tasks
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils import siren as siren_utils
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
    codir_report_is_enabled = FeatureToggle.ENABLE_CODIR_OFFERERS_REPORT.is_active()

    if day is None:
        day = datetime.date.today().day

    offerers = (
        offerers_models.Offerer.query.filter(
            offerers_models.Offerer.id % 28 == day - 1,
            offerers_models.Offerer.isActive,
            sa.not_(offerers_models.Offerer.isRejected),
            sa.not_(offerers_models.Offerer.isClosed),
            offerers_models.Offerer.siren.is_not(None),
            sa.not_(offerers_models.Offerer.siren.like(f"{siren_utils.NEW_CALEDONIA_SIREN_PREFIX}%")),
        )
        .options(sa_orm.load_only(offerers_models.Offerer.siren))
        .all()
    )

    logger.info("check_active_offerers will check %s offerers in cloud tasks today", len(offerers))

    _create_check_offerer_tasks(
        [offerer.siren for offerer in offerers], dry_run=dry_run, fill_in_codir_report=codir_report_is_enabled
    )

    for offerer in offerers:
        # Do not flood Sirene API (max. 30 per minute for the whole product)
        offerers_tasks.check_offerer_siren_task.delay(
            offerers_tasks.CheckOffererSirenRequest(
                siren=offerer.siren,
                close_or_tag_when_inactive=not dry_run,
                fill_in_codir_report=codir_report_is_enabled,
            )
        )


def _create_check_offerer_tasks(siren_list: list[str], *, dry_run: bool, fill_in_codir_report: bool = False) -> None:
    # Do not flood Sirene API (max. 30 per minute for the whole product)
    for siren in siren_list:
        payload = offerers_tasks.CheckOffererSirenRequest(
            siren=siren,
            close_or_tag_when_inactive=not dry_run,
            fill_in_codir_report=fill_in_codir_report,
        )
        offerers_tasks.check_offerer_siren_task.delay(payload)


@blueprint.cli.command("check_closed_offerers")
@click.option("--dry-run", type=bool, default=False)
@click.option("--date-closed", type=str, required=False, default=None)
def check_closed_offerers(dry_run: bool = False, date_closed: str | None = None) -> None:
    if date_closed:
        query_date = datetime.date.fromisoformat(date_closed)
    else:
        # Check closures registered two days before to ensure that the API database has already been updated.
        query_date = datetime.date.today() - datetime.timedelta(days=2)

    try:
        siren_list = sirene.get_siren_closed_at_date(query_date)
    except entreprise_exceptions.SireneException as exc:
        logger.error("Could not fetch closed SIREN from Sirene API", extra={"date": query_date.isoformat(), "exc": exc})
    else:
        known_siren_list = [
            siren
            for siren, in offerers_models.Offerer.query.filter(
                offerers_models.Offerer.siren.in_(siren_list),
                offerers_models.Offerer.isActive,
                sa.not_(offerers_models.Offerer.isRejected),
            )
            .with_entities(offerers_models.Offerer.siren)
            .all()
        ]

        logger.info(
            "check_closed_offerers found %s active SIREN which active/closed status has been updated on %s",
            len(known_siren_list),
            query_date.isoformat(),
            extra={"siren": known_siren_list},
        )

        _create_check_offerer_tasks(known_siren_list, dry_run=dry_run)

    # Scheduled SIREN
    scheduled_siren_list = offerers_tasks.get_scheduled_siren_to_check(
        query_date if date_closed else datetime.date.today()
    )
    if scheduled_siren_list:
        logger.info(
            "check_closed_offerers found %s scheduled SIREN to check on %s",
            len(scheduled_siren_list),
            query_date.isoformat(),
            extra={"siren": scheduled_siren_list},
        )
        _create_check_offerer_tasks(scheduled_siren_list, dry_run=dry_run)


@blueprint.cli.command("delete_user_offerers_on_closed_offerers")
@click.option("--dry-run", type=bool, default=False)
def delete_user_offerers_on_closed_offerers(dry_run: bool = False) -> None:
    offerers_api.auto_delete_attachments_on_closed_offerers()

    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()


@log_cron_with_transaction
@blueprint.cli.command("send_reminder_email_to_individual_offerers")
def send_reminder_email_to_individual_offerers() -> None:
    # This command is called from a cron running every day.
    offerers_api.send_reminder_email_to_individual_offerers()


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
@click.option("--batch-size", type=int, default=BATCH_SIZE, help="Size of venues batches to synchronize")
@click.option("--start-from-batch", type=int, default=1, help="Start synchronization from batch number")
def synchronize_accessibility_with_acceslibre(
    dry_run: bool = False, force_sync: bool = False, batch_size: int = BATCH_SIZE, start_from_batch: int = 1
) -> None:
    offerers_api.synchronize_accessibility_with_acceslibre(
        dry_run=dry_run, force_sync=force_sync, batch_size=batch_size, start_from_batch=start_from_batch
    )


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
