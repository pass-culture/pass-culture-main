import logging

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offerers import models
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


def cancel_venue_bookings(
    venue: models.Venue, author_id: int | None = None, user_connect_as: bool | None = None
) -> list[bookings_models.Booking]:
    stocks = [stock for offer in venue.offers for stock in offer.stocks]
    cancelled = []

    for stock in stocks:
        bookings = bookings_api.cancel_bookings_from_stock_by_offerer(stock, author_id, user_connect_as)

        for chunk in enumerate(get_chunks(bookings, 100)):
            logger.info(
                "closing venue: bookings cancelled",
                extra={
                    "venue": venue.id,
                    "offer": stock.offerId,
                    "stock": stock.id,
                    "bookings": {b.id for b in bookings},
                },
            )

        cancelled.extend(bookings)

    return bookings
