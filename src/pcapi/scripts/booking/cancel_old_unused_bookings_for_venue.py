from datetime import datetime, timedelta
from typing import List

from sqlalchemy.sql.sqltypes import DateTime
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.repository import repository
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.repository.venue_queries import find_by_id
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.logger import logger


def cancel_old_unused_bookings_for_venue(humanized_venue_id: str) -> None:
    venue_id = dehumanize(humanized_venue_id)
    if venue_id is None:
        return

    venue = find_by_id(venue_id)

    if venue is None:
        raise Exception(f"There is no venue with id {humanized_venue_id}")

    limit_date = datetime.now() - timedelta(days=30)

    old_unused_bookings = _get_old_unused_bookings_from_venue_id(venue.id, limit_date)

    for old_unused_booking in old_unused_bookings:
        old_unused_booking.isCancelled = True

    if len(old_unused_bookings) > 0:
        repository.save(*old_unused_bookings)
        logger.info(f"'{len(old_unused_bookings)}' bookings cancelled for venue '{venue.name}'")


def _get_old_unused_bookings_from_venue_id(venue_id: int, limit_date: DateTime) -> List[Booking]:
    return (
        Booking.query.join(StockSQLEntity, StockSQLEntity.id == Booking.stockId)
        .join(Offer, Offer.id == StockSQLEntity.offerId)
        .filter(Offer.venueId == venue_id)
        .filter(~Booking.isCancelled)
        .filter(~Booking.isUsed)
        .filter(Booking.dateCreated < limit_date)
        .all()
    )
