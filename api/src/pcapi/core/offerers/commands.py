import datetime
import logging
from math import ceil

import click
import pytz
import sqlalchemy as sa

import pcapi.connectors.acceslibre as accessibility_provider
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
def synchronize_accessibility_with_acceslibre(dry_run: bool = False, force_sync: bool = False) -> None:
    """
    For all venues synchronized with acceslibre, we fetch on a weekly basis the
    last_update_at and update their accessibility informations.

    If we use the --force_sync flag, it will not check for last_update_at

    If externalAccessibilityId can't be found at acceslibre, we try to find a new match
    """
    venues_count = (
        db.session.query(sa.func.count("*"))
        .select_from(sa.join(offerers_models.Venue, offerers_models.AccessibilityProvider))
        .filter(
            offerers_models.Venue.isPermanent == True,
            offerers_models.Venue.isVirtual == False,
            offerers_models.AccessibilityProvider.externalAccessibilityId.isnot(None),
        )
        .scalar()
    )
    num_batches = ceil(venues_count / BATCH_SIZE)
    for i in range(num_batches):
        venues_list = (
            offerers_models.Venue.query.join(offerers_models.Venue.accessibilityProvider)
            .filter(
                offerers_models.Venue.isPermanent == True,
                offerers_models.Venue.isVirtual == False,
                offerers_models.AccessibilityProvider.externalAccessibilityId.isnot(None),
            )
            .options(sa.orm.contains_eager(offerers_models.Venue.accessibilityProvider))
            .order_by(offerers_models.Venue.id.asc())
            .limit(BATCH_SIZE)
            .offset(i * BATCH_SIZE)
            .all()
        )
        for venue in venues_list:
            slug = venue.accessibilityProvider.externalAccessibilityId
            last_update = accessibility_provider.get_last_update_at_provider(slug=slug)
            # if last_update is not None: match still exist
            # Then we update accessibility data if :
            # 1. accessibility data is None
            # 2. we have forced the synchronization
            # 3. accessibility data has been updated on acceslibre side
            if last_update and (
                not venue.accessibilityProvider.externalAccessibilityData
                or force_sync
                or venue.accessibilityProvider.lastUpdateAtProvider.astimezone(pytz.utc)
                < last_update.astimezone(pytz.utc)
            ):
                venue.accessibilityProvider.lastUpdateAtProvider = last_update
                accessibility_data = accessibility_provider.get_accessibility_infos(
                    slug=venue.accessibilityProvider.externalAccessibilityId
                )
                venue.accessibilityProvider.externalAccessibilityData = (
                    accessibility_data.dict() if accessibility_data else None
                )
                db.session.add(venue.accessibilityProvider)

            # if last_update is None, the slug has been removed from acceslibre, we try a new match
            # and save accessibility data to DB
            elif not last_update:
                if id_and_url_at_provider := accessibility_provider.get_id_at_accessibility_provider(
                    name=venue.name,
                    public_name=venue.publicName,
                    siret=venue.siret,
                    ban_id=venue.banId,
                    city=venue.city,
                    postal_code=venue.postalCode,
                    address=venue.address,
                ):
                    new_slug = id_and_url_at_provider["slug"]
                    new_url = id_and_url_at_provider["url"]
                    if last_update := accessibility_provider.get_last_update_at_provider(slug=new_slug):
                        accessibility_data = accessibility_provider.get_accessibility_infos(slug=new_slug)
                        venue.accessibilityProvider.externalAccessibilityId = new_slug
                        venue.accessibilityProvider.externalAccessibilityUrl = new_url
                        venue.accessibilityProvider.lastUpdateAtProvider = last_update
                        venue.accessibilityProvider.externalAccessibilityData = (
                            accessibility_data.dict() if accessibility_data else None
                        )
                        db.session.add(venue.accessibilityProvider)
                else:
                    logger.info(
                        "Slug %s has not been found at acceslibre. Removing AccessibilityProvider %d",
                        slug,
                        venue.accessibilityProvider.id,
                    )
                db.session.delete(venue.accessibilityProvider)
        if not dry_run:
            try:
                db.session.commit()
            except sa.exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i)
                db.session.rollback()
        else:
            db.session.rollback()


@blueprint.cli.command("synchronize_venue_with_acceslibre")
@click.argument("venue_id", type=int, required=True, default=None)
def synchronize_venue_with_acceslibre(venue_id: int) -> None:
    venue = offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()
    offerers_api.set_accessibility_provider_id(venue)
    if not venue.accessibilityProvider.externalAccessibilityId:
        logger.info("No match found at acceslibre for Venue %s ", venue_id)
        return
    offerers_api.set_accessibility_last_update_at_provider(venue)
    offerers_api.set_accessibility_infos_from_provider_id(venue)
    db.session.add(venue)
    db.session.commit()
