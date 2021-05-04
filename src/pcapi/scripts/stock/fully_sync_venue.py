import logging

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.models import db
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def _reset_stock_quantity(venue: Venue) -> None:
    """Reset all stock quantity with the number of non-cancelled bookings."""
    query = """
      UPDATE stock
      SET quantity = "dnBookedQuantity"
      FROM offer
      WHERE
          offer."idAtProviders" IS NOT NULL
          AND offer.id = stock."offerId"
          AND offer."venueId" = :venue_id
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
