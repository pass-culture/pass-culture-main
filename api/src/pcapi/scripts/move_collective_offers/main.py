import argparse

import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.models import db


OLD_OFFERER_ID = 4239
OLD_VENUE_ID = 20896

NEW_OFFERER_ID = 13620
NEW_VENUE_ID = 147652


COLLECTIVE_BOOKING_IDS = [
    417396,
    525529,
    507049,
    525554,
    505722,
    551271,
    467440,
    431722,
    401296,
    478904,
    565584,
    478480,
    445393,
    448662,
    415065,
    399005,
    399004,
    577804,
    568317,
    445660,
    397676,
    558176,
    510539,
    545164,
    509898,
    416382,
    564563,
    443609,
    425672,
    540119,
    425674,
    455768,
    522046,
    577154,
    443327,
    444827,
    562667,
    576614,
]


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
            new_offer_venue_dict = collective_offer.offerVenue
            new_offer_venue_dict["venueId"] = NEW_VENUE_ID
            collective_offer.offerVenue = new_offer_venue_dict

            # those values are useless for now, and they're not present in the new offerer
            collective_offer.offererAddressId = None
            collective_offer.locationType = None

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
