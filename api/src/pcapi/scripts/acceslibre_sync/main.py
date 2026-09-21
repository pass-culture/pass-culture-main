"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=stg \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-43610-acceslibre-synch-script \
  -f NAMESPACE=acceslibre_sync \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from math import ceil

import pytz
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm

import pcapi.connectors.acceslibre as accessibility_provider
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def _count_open_to_public_venues_with_accessibility_provider() -> int:
    return (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.AccessibilityProvider)
        .filter(offerers_models.Venue.isOpenToPublic.is_(True))
        .count()
    )


def _count_open_to_public_venues_without_accessibility_provider() -> int:
    return (
        db.session.query(offerers_models.Venue)
        .outerjoin(offerers_models.Venue.accessibilityProvider)
        .filter(
            offerers_models.Venue.isOpenToPublic.is_(True),
            offerers_models.AccessibilityProvider.id.is_(None),
        )
        .count()
    )


def _get_open_to_public_venues_without_accessibility_provider(
    batch_size: int, batch_num: int
) -> list[offerers_models.Venue]:
    return (
        db.session.query(offerers_models.Venue)
        .outerjoin(offerers_models.Venue.accessibilityProvider)
        .filter(
            offerers_models.Venue.isOpenToPublic.is_(True),
            offerers_models.AccessibilityProvider.id.is_(None),
        )
        .options(
            sa_orm.load_only(
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
                offerers_models.Venue.isOpenToPublic,
            ),
            sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address),
        )
        .order_by(offerers_models.Venue.id.asc())
        .limit(batch_size)
        .offset(batch_num * batch_size)
        .all()
    )


def _get_open_to_public_venues_with_accessibility_provider(
    batch_size: int, batch_num: int
) -> list[offerers_models.Venue]:
    return (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.Venue.accessibilityProvider)
        .filter(offerers_models.Venue.isOpenToPublic.is_(True))
        .options(
            sa_orm.contains_eager(offerers_models.Venue.accessibilityProvider),
            sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address),
        )
        .order_by(offerers_models.Venue.id.asc())
        .limit(batch_size)
        .offset(batch_num * batch_size)
        .all()
    )


def _synchronize_accessibility_provider(venue: offerers_models.Venue, force_sync: bool = False) -> None:
    assert venue.accessibilityProvider  # helps mypy, ensured by caller
    assert venue.offererAddress and venue.offererAddress.address  # helps mypy, shouldn't happen
    slug = venue.accessibilityProvider.externalAccessibilityId
    try:
        last_update, accessibility_data = accessibility_provider.get_accessibility_infos(slug=slug)
    except accessibility_provider.AccesLibreApiException as e:
        logger.exception("An error occurred while requesting Acceslibre widget for venue: %s, Error: %s", venue, e)
        return

    # If last_update is not None: match still exist
    # Then we update accessibility data if :
    # 1. accessibility data is None
    # 2. we have forced the synchronization
    # 3. accessibility data has been updated on acceslibre side
    if last_update and (
        not venue.accessibilityProvider.externalAccessibilityData
        or force_sync
        or venue.accessibilityProvider.lastUpdateAtProvider.astimezone(pytz.utc) < last_update.astimezone(pytz.utc)
    ):
        venue.accessibilityProvider.lastUpdateAtProvider = last_update
        venue.accessibilityProvider.externalAccessibilityData = (
            accessibility_data.dict() if accessibility_data else None
        )

    # if last_update is None, the slug has been removed from acceslibre, we try a new match
    # and save accessibility data to DB
    elif not last_update:
        try:
            id_and_url_at_provider = accessibility_provider.get_id_at_accessibility_provider(
                name=venue.name,
                public_name=venue.publicName,
                siret=venue.siret,
                ban_id=venue.offererAddress.address.banId,
                city=venue.offererAddress.address.city,
                postal_code=venue.offererAddress.address.postalCode,
                address=venue.offererAddress.address.street,
            )
        except accessibility_provider.AccesLibreApiException as e:
            logger.exception("An error occurred while requesting Acceslibre for venue: %s, Error: %s", venue, e)
            return
        if id_and_url_at_provider:
            new_slug = id_and_url_at_provider["slug"]
            new_url = id_and_url_at_provider["url"]
            try:
                last_update, accessibility_data = accessibility_provider.get_accessibility_infos(slug=new_slug)
            except accessibility_provider.AccesLibreApiException as e:
                logger.exception(
                    "An error occurred while requesting Acceslibre widget for venue: %s, Error: %s", venue, e
                )
                return
            if last_update and accessibility_data:
                venue.accessibilityProvider.externalAccessibilityId = new_slug
                venue.accessibilityProvider.externalAccessibilityUrl = new_url
                venue.accessibilityProvider.lastUpdateAtProvider = last_update
                venue.accessibilityProvider.externalAccessibilityData = (
                    accessibility_data.dict() if accessibility_data else None
                )
                logger.info(
                    "Acceslibre update synchronisation",
                    extra={
                        "analyticsSource": "app-pro",
                        "venue_id": venue.id,
                        "acceslibre_slug": slug,
                        "update_message": "New slug found at acceslibre for already synchronized venue",
                    },
                    technical_message_id="acceslibre.synchronisation.update",
                )
        else:
            logger.info(
                "Acceslibre synchronisation loss",
                extra={
                    "analyticsSource": "app-pro",
                    "venue_id": venue.id,
                    "acceslibre_slug": slug,
                    "update_message": "Slug not found at acceslibre, AccessibilityProvider removed for this venue",
                },
                technical_message_id="acceslibre.synchronisation.lost",
            )
            db.session.delete(venue.accessibilityProvider)

    # In case a venue is synchronized but has no data, we want to be informed
    if venue.accessibilityProvider and not venue.accessibilityProvider.externalAccessibilityData:
        logger.error(
            "Venue %s is synchronized with Acceslibre at %s but has no data",
            venue.id,
            venue.accessibilityProvider.externalAccessibilityData,
        )


def _synchronize_accessibility_with_acceslibre(
    apply: bool, force_sync: bool, batch_size: int, start_from_batch: int = 1
) -> None:
    """
    For all venues synchronized with acceslibre, we fetch on a weekly basis the
    last_update_at and update their accessibility information.

    If we use the --force_sync flag, it will not check for last_update_at

    If we use the --start-from-batch option, it will start synchronization from the given batch number
    Use case: synchronization has failed with message "Could not update batch <n>"

    If externalAccessibilityId can't be found at acceslibre, we try to find a new match, cf. synchronize_accessibility_provider()
    """
    logger.info("Starting acceslibre synchronisation")

    venues_count = _count_open_to_public_venues_with_accessibility_provider()
    num_batches = ceil(venues_count / batch_size)
    if start_from_batch > num_batches:
        logger.error("Start from batch must be less than %d", num_batches)
        return

    start_batch_index = start_from_batch - 1
    for i in range(start_batch_index, num_batches):
        venues_list = _get_open_to_public_venues_with_accessibility_provider(batch_size=batch_size, batch_num=i)
        for venue in venues_list:
            _synchronize_accessibility_provider(venue, force_sync)

        if apply:
            try:
                db.session.commit()
            except sa.exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i + 1)
                db.session.rollback()
        else:
            db.session.rollback()

        db.session.expunge_all()

    logger.info("Accessibility data synchronization with acceslibre complete successfully")


def _match_venue_with_new_entries(
    venues_list: list[offerers_models.Venue],
    results: list,
) -> None:
    for venue in venues_list:
        assert venue.offererAddress and venue.offererAddress.address  # helps mypy, shouldn't happen
        if matching_venue := accessibility_provider.match_venue_with_acceslibre(
            acceslibre_results=results,
            venue_name=venue.name,
            venue_public_name=venue.publicName,
            venue_address=venue.offererAddress.address.street,
            venue_city=venue.offererAddress.address.city,
            venue_postal_code=venue.offererAddress.address.postalCode,
            venue_ban_id=venue.offererAddress.address.banId,
            venue_siret=venue.siret,
        ):
            venue.accessibilityProvider = offerers_models.AccessibilityProvider(
                externalAccessibilityId=matching_venue.slug,
                externalAccessibilityUrl=matching_venue.web_url,
            )
            db.session.add(venue.accessibilityProvider)


def _acceslibre_matching(batch_size: int, apply: bool, start_from_batch: int, n_days_to_fetch: int = 7) -> None:
    """
    For all venues opened to public, we are looking for a match at acceslibre

    If we use the --start-from-batch option, it will start synchronization from the given batch number
    Use case: synchronization has failed with message "Could not update batch <n>"
    """
    synchronized_venues_count_before_matching = _count_open_to_public_venues_with_accessibility_provider()
    total_venues_without_provider = _count_open_to_public_venues_without_accessibility_provider()
    num_batches = ceil(total_venues_without_provider / batch_size)
    if start_from_batch > num_batches:
        logger.info("Start from batch must be less than %d", num_batches)
        return

    results_list = []
    for activity in accessibility_provider.AcceslibreActivity:
        if results_by_activity := accessibility_provider.find_new_entries_by_activity(activity, n_days_to_fetch):
            results_list.extend(results_by_activity)

    start_batch_index = start_from_batch - 1
    for i in range(start_batch_index, num_batches):
        venues_batch = _get_open_to_public_venues_without_accessibility_provider(batch_size=batch_size, batch_num=i)

        _match_venue_with_new_entries(venues_batch, results_list)

        if apply:
            try:
                db.session.commit()
            except sa_exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i + 1)
                db.session.rollback()
        else:
            db.session.rollback()

    new_match_found = (
        _count_open_to_public_venues_with_accessibility_provider() - synchronized_venues_count_before_matching
    )
    logger.info("%d new match found over last %d days", new_match_found, n_days_to_fetch)
    if apply:
        logger.info("Matching with acceslibre complete")
    else:
        logger.info("Matching with acceslibre as dry run complete")
        db.session.rollback()


def main(apply: bool, force_sync: bool, batch_size: int, start_from_batch: int, n_days_to_fetch: int) -> None:
    logger.info("starting synchronization")

    _synchronize_accessibility_with_acceslibre(
        apply=apply,
        force_sync=force_sync,
        batch_size=batch_size,
        start_from_batch=start_from_batch,
    )

    logger.info("synchronization successfully finished")

    logger.info("starting finding new match")
    _acceslibre_matching(
        batch_size=batch_size,
        apply=apply,
        start_from_batch=start_from_batch,
        n_days_to_fetch=n_days_to_fetch,
    )
    logger.info("finding new match successfully finished")


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()

    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force-sync", action="store_true")
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--start-from-batch", type=int, default=1)
    parser.add_argument("--n-days-to-fetch", type=int, default=7)

    args = parser.parse_args()

    main(
        apply=args.apply,
        force_sync=args.force_sync,
        batch_size=args.batch_size,
        start_from_batch=args.start_from_batch,
        n_days_to_fetch=args.n_days_to_fetch,
    )

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
