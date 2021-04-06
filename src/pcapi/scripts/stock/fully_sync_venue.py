import logging

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.models import db
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def _reset_stock_quantity(venue: Venue) -> None:
    query = """
      WITH bookings_per_stock AS (
        SELECT
          stock.id AS stock_id,
          COALESCE(SUM(booking.quantity), 0) AS total_bookings
        FROM stock
        JOIN offer ON offer.id = stock."offerId"
        -- The `NOT isCancelled` condition MUST be part of the JOIN.
        -- If it were part of the WHERE clause, that would exclude
        -- stocks that only have cancelled bookings.
        LEFT OUTER JOIN booking
          ON booking."stockId" = stock.id
          AND NOT booking."isCancelled"
        WHERE offer."venueId" = :venue_id
        GROUP BY stock.id
      )
      UPDATE stock
      SET quantity = bookings_per_stock.total_bookings
      FROM bookings_per_stock
      WHERE stock.id = bookings_per_stock.stock_id
    """
    db.session.execute(query, {"venue_id": venue.id})
    db.session.commit()


def fully_sync_venue(venue: Venue) -> None:
    logger.info("Resetting all stock quantity for full resync", extra={"venue": venue.id})
    _reset_stock_quantity(venue)

    venue_provider = VenueProvider.query.filter_by(venueId=venue.id).one()
    venue_provider.lastSyncDate = None
    repository.save(venue_provider)

    synchronize_venue_provider(venue_provider)
