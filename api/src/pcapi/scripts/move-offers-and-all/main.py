"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39757-move-offers-from-siret-to-other \
  -f NAMESPACE=move-offers-and-all \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from flask_login import current_user

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.api import get_or_create_offer_location
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(old_venue_id: int, new_venue_id: int) -> None:
    old_venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == old_venue_id).one()
    new_venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == new_venue_id).one()

    offers = db.session.query(offers_models.Offer).filter(offers_models.Offer.venueId == old_venue_id).all()
    logger.info("Found %s offers to move", len(offers))
    for offer in offers:
        offer.venueId = new_venue_id
        offer.offererAddressId = get_or_create_offer_location(
            new_venue.managingOffererId, offer.offererAddress.addressId, label=offer.offererAddress.label
        ).id
        db.session.add(offer)

    bookings = (
        db.session.query(bookings_models.Booking)
        .filter(
            bookings_models.Booking.venueId == old_venue_id,
            bookings_models.Booking.status.in_(
                [bookings_models.BookingStatus.CONFIRMED, bookings_models.BookingStatus.USED]
            ),
        )
        .all()
    )

    finance_events: set[finance_models.FinanceEvent] = set()
    pricings: set[finance_models.Pricing] = set()

    logger.info("Found %s bookings to move", len(bookings))
    for booking in bookings:
        booking.venueId = new_venue_id
        booking.offererId = new_venue.managingOffererId
        db.session.add(booking)
        finance_events.update(booking.finance_events)
        pricings.update(booking.pricings)

    logger.info("Found %s finance events to move", len(finance_events))
    for event in finance_events:
        event.venueId = new_venue_id
        event.pricingPointId = new_venue_id
        db.session.add(event)

    logger.info("Found %s pricings to move", len(pricings))
    for pricing in finance_events:
        pricing.venueId = new_venue_id
        pricing.pricingPointId = new_venue_id
        db.session.add(pricing)

    history_api.add_action(
        history_models.ActionType.COMMENT,
        author=current_user,
        venue=old_venue,
        comment=("PC-39757 - Offres et réservations en cours déplacées vers la venue %s", new_venue_id),
    )
    history_api.add_action(
        history_models.ActionType.COMMENT,
        author=current_user,
        venue=new_venue,
        comment=("PC-39757 - Offres et réservations en cours importées depuis la venue %s", old_venue_id),
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--old-venue-id", required=True, type=int)
    parser.add_argument("--new-venue-id", required=True, type=int)
    args = parser.parse_args()

    main(args.old_venue_id, args.new_venue_id)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
