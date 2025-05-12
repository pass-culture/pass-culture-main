import argparse
import logging

from pcapi.app import app
import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db


OFFER_IDS = [314633153, 313878285]

logger = logging.getLogger(__name__)


def main(offer_id: int) -> None:
    bookings = (
        db.session.query(bookings_models.Booking)
        .join(offers_models.Stock, offers_models.Stock.id == bookings_models.Booking.stockId)
        .join(offers_models.Offer, offers_models.Offer.id == offers_models.Stock.offerId)
        .filter(offers_models.Offer.id == offer_id, bookings_models.Booking.cancellationLimitDate.is_(None))
    ).all()
    logger.info(f"{len(bookings)} bookings to update")

    for booking in bookings:
        booking.cancellationLimitDate = bookings_api.compute_booking_cancellation_limit_date(
            booking.stock.beginningDatetime, booking.dateCreated
        )
        db.session.add(booking)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()
    for offer_id in OFFER_IDS:
        main(offer_id)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
