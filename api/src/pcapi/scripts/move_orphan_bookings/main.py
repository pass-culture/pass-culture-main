"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37712-api-le-venue-104076-est-soft-delete-mais-il-a-encore-des-reservations/api/src/pcapi/scripts/move_orphan_offers/main.py

"""

import argparse
import logging

import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.models as offer_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(dry_run: bool) -> None:
    offer_id = 103_855_154
    original_venue_id = 104_076
    destination_venue_id = 104_071
    bookings_ids = (
        db.session.query(bookings_models.Booking)
        .with_entities(bookings_models.Booking.id)
        .join(bookings_models.Booking.stock)
        .filter(
            offer_models.Stock.offerId == offer_id,
            bookings_models.Booking.venueId == original_venue_id,
        )
        .limit(10_000)
    )
    bookings = db.session.query(bookings_models.Booking).filter(bookings_models.Booking.id.in_(bookings_ids))
    count = bookings.update({"venueId": destination_venue_id}, synchronize_session=False)
    logger.info(f"Moved {count} bookings from venue {original_venue_id} to venue {destination_venue_id}")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()
    dry_run = not args.not_dry

    main(dry_run=dry_run)

    if dry_run:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
    else:
        logger.info("Finished")
        db.session.commit()
