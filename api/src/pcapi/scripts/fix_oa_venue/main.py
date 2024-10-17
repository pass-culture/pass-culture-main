import argparse
import logging

import psycopg2
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from pcapi.app import app
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)


app.app_context().push()


def fix_oa_venues(dry_run: bool = True) -> None:
    offerer_addresses_with_multiple_venues = (
        db.session.query(OffererAddress)
        .join(Venue, Venue.offererAddressId == OffererAddress.id)
        .group_by(OffererAddress.id)
        .having(sa.func.count(Venue.id) > 1)
        .all()
    )

    logger.info("Found %s OffererAddresses with multiple Venues", str(len(offerer_addresses_with_multiple_venues)))
    for offerer_address in offerer_addresses_with_multiple_venues:
        logger.info("processing OffererAddress %s", offerer_address.id)
        venues = db.session.query(Venue).filter(Venue.offererAddressId == offerer_address.id).all()
        for venue in venues[1:]:
            # Create a new OffererAddress with label set to Venue.common_name
            try:
                new_offerer_address = OffererAddress(
                    offererId=offerer_address.offererId,
                    label=venue.common_name,
                    address=offerer_address.address,
                )
                db.session.add(new_offerer_address)
                db.session.flush()  # Ensure the new OffererAddress gets an ID
                db.session.add(venue)
                venue.offererAddressId = new_offerer_address.id
            except psycopg2.errors.UniqueViolation:
                db.session.rollback()
                logger.error("Error while processing OffererAddress: %s ", offerer_address.id)

            except IntegrityError:
                db.session.rollback()
                logger.error("IntegrityError while processing OffererAddress : %s", offerer_address.id)

        if not dry_run:
            db.session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="mais qui va lire ça ?")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        fix_oa_venues(args.dry_run)
    except:
        db.session.rollback()
        raise
    if args.dry_run:
        db.session.rollback()
