import argparse
import logging

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()
OFFER_BATCH_SIZE = 500


def create_offerer_address_for_venues(dry_run: bool = True) -> None:
    db.session.execute("set statement_timeout = '600s'")
    offerer_addresses_with_multiple_venues = (
        OffererAddress.query.join(Venue, Venue.offererAddressId == OffererAddress.id)
        .group_by(OffererAddress.id)
        .having(db.func.count(Venue.id) > 1)
        .options(sa.orm.selectinload(OffererAddress.venues))
        .all()
    )
    logger.info("Found %s OffererAddresses with multiple Venues", str(len(offerer_addresses_with_multiple_venues)))
    for offerer_address in offerer_addresses_with_multiple_venues:
        venues_subquery = (
            Venue.query.filter(Venue.offererAddressId == offerer_address.id)
            .outerjoin(Offer, Venue.id == Offer.venueId)
            .group_by(Venue.id)
            .order_by(sa.func.count(Offer.id).desc())
            .with_entities(Venue.id)
            .subquery()
        )
        venues = (
            Venue.query.join(venues_subquery, Venue.id == venues_subquery.c.id)
            .options(
                sa.orm.load_only(Venue.id, Venue.publicName, Venue.name),
                sa.orm.joinedload(Venue.offererAddress).joinedload(OffererAddress.address),
            )
            .all()
        )
        logger.info("Processing OffererAddress %s", offerer_address.id)
        for venue in venues[1:]:
            logger.info("Processing Venue %s", venue.id)

            new_offerer_address = OffererAddress(
                offererId=venue.managingOffererId, label=None, address=venue.offererAddress.address
            )
            db.session.add(new_offerer_address)
            db.session.flush()
            venue.offererAddressId = new_offerer_address.id
            venue.offererAddress = new_offerer_address
            db.session.add(venue)
            offers_query = (
                Offer.query.filter(Offer.venueId == venue.id, Offer.offererAddressId == offerer_address.id)
                .with_entities(Offer.id)
                .yield_per(1000)
            )
            db.session.bulk_update_mappings(
                Offer, [{"id": offer.id, "offererAddressId": new_offerer_address.id} for offer in offers_query]
            )
            if dry_run:
                db.session.rollback()
            else:
                db.session.commit()
    db.session.execute(
        sa.text("""SET SESSION statement_timeout = :timeout ;"""), {"timeout": settings.DATABASE_STATEMENT_TIMEOUT}
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parser for fixing venues offerer address")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        create_offerer_address_for_venues(args.dry_run)
    except:
        db.session.rollback()
        raise

    if args.dry_run:
        db.session.rollback()
