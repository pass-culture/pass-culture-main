"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43601-move-booking-to-their-offerer \
  -f NAMESPACE=move_booking_to_offerer \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.bookings import models as bookings_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(venue_id: int) -> None:
    venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_id).one()
    db.session.query(bookings_models.Booking).filter(
        bookings_models.Booking.venueId == venue_id, bookings_models.Booking.offererId != venue.managingOffererId
    ).update({bookings_models.Booking.offererId: venue.managingOffererId})


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--venue-id", required=True, type=int)
    args = parser.parse_args()

    main(args.venue_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
