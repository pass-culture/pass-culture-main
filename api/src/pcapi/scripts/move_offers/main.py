"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-41733-move-offers \
  -f NAMESPACE=move_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(old_venue_id: int, new_venue_id: int) -> None:
    old_venue = db.session.query(offerers_models.Venue).filter_by(id=old_venue_id).one()
    logger.info("Old venue: %d - %s", old_venue.id, old_venue.publicName)

    new_venue = db.session.query(offerers_models.Venue).filter_by(id=new_venue_id).one()
    logger.info("New venue: %d - %s", new_venue.id, new_venue.publicName)

    assert (
        db.session.query(bookings_models.Booking)
        .filter(
            bookings_models.Booking.venueId == old_venue_id,
            bookings_models.Booking.status.not_in(
                [bookings_models.BookingStatus.REIMBURSED, bookings_models.BookingStatus.CANCELLED]
            ),
        )
        .count()
        == 0
    )
    assert (
        db.session.query(offers_models.PriceCategoryLabel)
        .filter(offers_models.PriceCategoryLabel.venueId == old_venue_id)
        .count()
        == 0
    )
    logger.info("Checked bookings and price category labels: OK")

    offers = db.session.query(offers_models.Offer).filter(offers_models.Offer.venueId == old_venue_id).all()
    logger.info("%d offers found for venue %d", len(offers), old_venue_id)

    for offer in offers:
        offer.venue = new_venue
        if offer.offererAddress:
            new_location = offerers_api.get_or_create_offer_location(
                new_venue.managingOffererId,
                offer.offererAddress.addressId,
                venue_id=new_venue.id,
                label=new_venue.publicName,
            )
            offer.offererAddress = new_location
        logging.info("Move offer %d to venue %d with OA %d", offer.id, new_venue.id, offer.offererAddressId)
        db.session.add(offer)

    db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--old-venue-id", type=int, required=True)
    parser.add_argument("--new-venue-id", type=int, required=True)
    args = parser.parse_args()

    main(args.old_venue_id, args.new_venue_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
