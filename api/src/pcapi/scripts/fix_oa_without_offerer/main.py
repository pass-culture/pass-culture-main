import argparse
import datetime
import logging
import random
import string

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
from pcapi.core.educational import models as educational_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db


app.app_context().push()
logger = logging.getLogger(__name__)

DESCRIPTION = "Fix incorrect OffererAddresses without offerer_id"
DEFAULT_TIMEOUT = "400s"


def find_items_to_fix() -> tuple:
    locations_to_update = []
    locations_to_delete = []
    errors = []

    incorrect_locations: set[offerers_models.OffererAddress] = set(
        db.session.scalars(
            sa.select(offerers_models.OffererAddress).where(
                offerers_models.OffererAddress.offererId == None  # pylint: disable=singleton-comparison
            )
        )
    )

    for location in incorrect_locations:
        linked_venues = set(
            db.session.execute(
                sa.select(offerers_models.Venue.id, offerers_models.Venue.managingOffererId)
                .where(offerers_models.Venue.offererAddressId == location.id)
                .distinct(offerers_models.Venue.id)
            )
        )

        if len(linked_venues) > 1:
            # OA is linked to several Venues
            # => OA should be corrected on a case by case basis
            errors.append(f"OA {location.id} linked to several Venues: { {item[0] for item in linked_venues} }")
        else:
            offers_venues = set()
            individual_offers_result = db.session.execute(
                sa.select(offers_models.Offer.venueId, offerers_models.Venue.managingOffererId)
                .join(offers_models.Offer.venue)
                .where(offers_models.Offer.offererAddressId == location.id)
                .distinct(offers_models.Offer.venueId)
            )
            offers_venues.update(set(individual_offers_result))
            collective_offers_result = db.session.execute(
                sa.select(educational_models.CollectiveOffer.venueId, offerers_models.Venue.managingOffererId)
                .join(educational_models.CollectiveOffer.venue)
                .where(educational_models.CollectiveOffer.offererAddressId == location.id)
                .distinct(educational_models.CollectiveOffer.venueId)
            )
            offers_venues.update(set(collective_offers_result))

            all_location_venues = linked_venues | offers_venues
            if len(all_location_venues) == 0:
                # OA is linked to no Venue
                # OA is used by no Offer and no CollectiveOffer
                # => OA is useless and can be deleted
                locations_to_delete.append(location.id)
            elif len(all_location_venues) == 1 or (
                len(linked_venues) == 0 and len({item[1] for item in offers_venues}) == 1
            ):
                # OA is either:
                # - linked to only one Venue and used by no Offers/CollectiveOffers
                # - linked to only one Venue and used by Offers/CollectiveOffers from only that Venue
                # - linked to no Venue and used by Offers/CollectiveOffers from only one Venue
                # - linked to no Venue and used by Offers/CollectiveOffers from several Venues but only one Offerer
                # => OA belongs to a unique Offerer and can be corrected
                location.offererId = all_location_venues.pop()[1]
                location.label = None
                locations_to_update.append(location)
            else:
                # OA is either:
                # - linked to one Venue but used by Offers/CollectiveOffers from other Venue(s)
                # - linked to no Venue but used by Offers/CollectiveOffers from several different Offerers
                # => OA should be corrected on a case by case basis
                errors.append(
                    f"OA {location.id} linked to or used in Offers/CollectiveOffers from several Venues: { {item[0] for item in all_location_venues} }"
                )

    return locations_to_update, locations_to_delete, errors


def update_items(items_to_update: set[offerers_models.OffererAddress]) -> None:
    try:
        if len(items_to_update) > 0:
            db.session.add_all(items_to_update)
        logger.info(
            "FIXED: Found %s OffererAddresses to fix",
            len(items_to_update),
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.info(
            "NOT CORRECTED: OffererAddresses could not be fixed - %s",
            str(e),
        )


def delete_items(ids_to_delete: set[int]) -> None:
    try:
        if len(ids_to_delete) > 0:
            offerers_models.OffererAddress.query.filter(
                offerers_models.OffererAddress.id.in_(ids_to_delete),
            ).delete()
        logger.info(
            "DELETED: Found %s OffererAddresses to delete",
            len(ids_to_delete),
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.info(
            "NOT DELETED: OffererAddresses could not be deleted - %s",
            str(e),
        )


def apply_script(timeout: str, dry_run: bool) -> None:
    run_id = "".join(random.choices(string.ascii_letters, k=5))
    start_time = datetime.datetime.utcnow()
    logger.info("Starting script run #%s at %s", run_id, start_time)
    try:
        db.session.execute(
            sa.text("Set session statement_timeout = :timeout"),
            {"timeout": timeout},
        )

        locations_to_update, locations_to_delete, errors = find_items_to_fix()
        update_items(locations_to_update)
        delete_items(locations_to_delete)
        if len(errors) > 0:
            logger.warning("NOT TREATED: Found %s OffererAdresses in error: %s", len(errors), errors)

    finally:
        db.session.execute(
            sa.text("Set session statement_timeout = :timeout"),
            {"timeout": settings.DATABASE_STATEMENT_TIMEOUT},
        )

    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()

    end_time = datetime.datetime.utcnow()
    logger.info(
        "Ending script run #%s at %s. Total run time: %s",
        run_id,
        end_time,
        end_time - start_time,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--timeout", type=str, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    try:
        apply_script(args.timeout, args.dry_run)

    except:
        db.session.rollback()
        raise
    if args.dry_run:
        db.session.rollback()
