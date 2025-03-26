import argparse

import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.models import db


OLD_OFFERER_ID = 25144
OLD_VENUE_ID = 61082

NEW_OFFERER_ID = 11185
NEW_VENUE_ID = 121926


COLLECTIVE_BOOKING_IDS = [530013, 528880, 545561, 551256, 551253, 545337, 531474, 531473, 548237, 531472, 546906]


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
        assert collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED

        collective_booking.offererId = NEW_OFFERER_ID
        collective_booking.venueId = NEW_VENUE_ID

        collective_offer = collective_booking.collectiveStock.collectiveOffer
        collective_offer.venueId = NEW_VENUE_ID

        # checked for these 11 offers, no need to migrate these columns:
        assert collective_offer.offerVenue["venueId"] is None
        assert collective_offer.offererAddressId is None
        assert collective_offer.templateId is None

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
