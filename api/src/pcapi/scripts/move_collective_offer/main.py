import argparse

import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.models import db


OLD_OFFERER_ID = 10636
OLD_VENUE_ID = 24515

NEW_OFFERER_ID = 18950
NEW_VENUE_ID = 44963


COLLECTIVE_BOOKING_IDS = [560059, 552032, 527487, 549820]


def move_collective_offers(do_update: bool) -> None:
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

    print(f"{len(collective_bookings)}/{len(COLLECTIVE_BOOKING_IDS)} collective bookings found")

    for collective_booking in collective_bookings:
        if collective_booking.status in {
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.PENDING,
        }:
            collective_booking.offererId = NEW_OFFERER_ID
            collective_booking.venueId = NEW_VENUE_ID

            collective_offer = collective_booking.collectiveStock.collectiveOffer
            collective_offer.venueId = NEW_VENUE_ID

            # those values are useless for now, and they're not present in the new offerer
            collective_offer.offererAddressId = None
            collective_offer.locationType = None

            if collective_offer.offerVenue["venueId"] == OLD_VENUE_ID:
                collective_offer.offerVenue["venueId"] = NEW_VENUE_ID

            db.session.add(collective_booking)
            db.session.add(collective_offer)

    db.session.flush()

    if do_update:
        db.session.commit()
        print("Committed.")
    else:
        db.session.rollback()
        print("Dry run finished.")


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Move collective offers")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    move_collective_offers(args.not_dry)
