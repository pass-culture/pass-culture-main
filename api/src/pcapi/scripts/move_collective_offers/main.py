"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=move_collective_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


OLD_OFFERER_ID = 14327
OLD_VENUE_ID = 33688

NEW_OFFERER_ID = 62584
NEW_VENUE_ID = 154642


COLLECTIVE_BOOKING_IDS = [
    635470,
    606589,
    635469,
    635468,
    606591,
    635466,
    635463,
    635453,
    606587,
]


def move_collective_offers() -> None:
    old_venue = db.session.query(offerers_models.Venue).filter_by(id=OLD_VENUE_ID).one()
    assert old_venue.managingOffererId == OLD_OFFERER_ID

    new_venue = db.session.query(offerers_models.Venue).filter_by(id=NEW_VENUE_ID).one()
    assert new_venue.managingOffererId == NEW_OFFERER_ID

    collective_bookings = (
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.id.in_(COLLECTIVE_BOOKING_IDS),
            educational_models.CollectiveBooking.offererId == OLD_OFFERER_ID,
            educational_models.CollectiveBooking.venueId == OLD_VENUE_ID,
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveOffer
            )
        )
        .all()
    )

    logger.info("%d/%d collective bookings found", len(collective_bookings), len(COLLECTIVE_BOOKING_IDS))

    for collective_booking in collective_bookings:
        if collective_booking.status in {
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.PENDING,
        }:
            collective_offer = collective_booking.collectiveStock.collectiveOffer
            logger.info("Moving collective booking %d, offer %d", collective_booking.id, collective_offer.id)

            collective_booking.offererId = NEW_OFFERER_ID
            collective_booking.venueId = NEW_VENUE_ID
            collective_offer.venueId = NEW_VENUE_ID

            if collective_offer.offererAddress:
                collective_offer.offererAddress = offerers_api.get_or_create_offer_location(
                    NEW_OFFERER_ID, collective_offer.offererAddress.addressId, label=old_venue.publicName
                )

            db.session.add(collective_booking)
            db.session.add(collective_offer)

    db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="Move collective offers")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    move_collective_offers()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
