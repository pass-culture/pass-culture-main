import argparse
import datetime
import logging
import random
import string

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
import pcapi.core.geography.models as geography_models
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


app.app_context().push()
logger = logging.getLogger(__name__)

DESCRIPTION = "Fix incorrect OffererAddresses (with incorrect Addresses) linked to several Venues"
DEFAULT_TIMEOUT = "400s"
INCORRECT_OA_IDS = [103425, 103535]


def fix_items(ids_to_fix: list[int]) -> list[offerers_models.Venue]:
    venues_to_update = []

    incorrect_locations: set[offerers_models.OffererAddress] = set(
        db.session.scalars(
            sa.select(offerers_models.OffererAddress).where(offerers_models.OffererAddress.id.in_(ids_to_fix))
        )
    )

    for location in incorrect_locations:
        linked_venues: set[offerers_models.Venue] = set(
            db.session.scalars(
                sa.select(offerers_models.Venue)
                .where(offerers_models.Venue.offererAddressId == location.id)
                .distinct(offerers_models.Venue.id)
            )
        )

        for venue in linked_venues:
            assert venue.street is not None
            assert venue.postalCode is not None
            assert venue.city is not None
            assert venue.departementCode is not None
            assert venue.latitude is not None
            assert venue.longitude is not None
            new_address = geography_models.Address(
                street=venue.street,
                postalCode=venue.postalCode,
                city=venue.city,
                departmentCode=venue.departementCode,
                latitude=venue.latitude,
                longitude=venue.longitude,
                isManualEdition=True,
            )
            new_location = offerers_models.OffererAddress(offerer=venue.managingOfferer, address=new_address)
            venue.offererAddress = new_location
            venues_to_update.append(venue)

    return venues_to_update


def apply_script(incorrect_ids: list[int], timeout: str, dry_run: bool) -> None:
    run_id = "".join(random.choices(string.ascii_letters, k=5))
    start_time = datetime.datetime.utcnow()
    logger.info("Starting script run #%s at %s", run_id, start_time)
    try:
        db.session.execute(
            sa.text("Set session statement_timeout = :timeout"),
            {"timeout": timeout},
        )

        venues_to_update = fix_items(incorrect_ids)
        try:
            if len(venues_to_update) > 0:
                db.session.add_all(venues_to_update)
            logger.info(
                "FIXED: Found %s Venues to fix",
                len(venues_to_update),
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.info(
                "NOT CORRECTED: Venues could not be fixed - %s",
                str(e),
            )

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
    parser.add_argument("--oa-ids", type=list, default=INCORRECT_OA_IDS)
    args = parser.parse_args()

    try:
        apply_script(args.oa_ids, args.timeout, args.dry_run)

    except:
        db.session.rollback()
        raise
    if args.dry_run:
        db.session.rollback()
