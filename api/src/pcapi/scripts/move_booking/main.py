"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-43341-move-bookings \
  -f NAMESPACE=move_booking \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def move_booking(booking_id: int, destination_venue_id: int) -> None:
    destination_venue = db.session.query(offerers_models.Venue).filter_by(id=destination_venue_id).one()
    booking = db.session.query(bookings_models.Booking).filter_by(id=booking_id).one()

    logging.info(
        "Move booking %s from venue %d to venue %d",
        booking.token,
        booking.venueId,
        destination_venue_id,
        extra={"booking_id": booking.id},
    )

    assert booking.offererId == destination_venue.managingOffererId
    assert booking.status == bookings_models.BookingStatus.USED

    booking.venueId = destination_venue_id
    db.session.add(booking)

    pricing = db.session.query(finance_models.Pricing).filter_by(bookingId=booking.id).one()
    db.session.query(finance_models.PricingLine).filter_by(pricingId=pricing.id).delete(synchronize_session=False)
    db.session.delete(pricing)

    finance_event = db.session.query(finance_models.FinanceEvent).filter_by(bookingId=booking.id).one()
    finance_event.venueId = destination_venue.id
    finance_event.pricingPointId = destination_venue.current_pricing_point_id
    finance_event.status = finance_models.FinanceEventStatus.READY
    finance_event.pricingOrderingDate = date_utils.get_naive_utc_now()
    db.session.add(finance_event)

    db.session.flush()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--booking-id", type=int, required=True)
    parser.add_argument("--destination-venue-id", type=int, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    move_booking(args.booking_id, args.destination_venue_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
