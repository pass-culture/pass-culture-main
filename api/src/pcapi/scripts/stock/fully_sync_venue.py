import logging

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.api import reset_stock_quantity
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def fully_sync_venue(venue: Venue) -> None:
    logger.info("Resetting all stock quantity for full resync", extra={"venue": venue.id})
    reset_stock_quantity(venue)

    venue_provider = VenueProvider.query.filter_by(venueId=venue.id, isActive=True).one()
    venue_provider.lastSyncDate = None
    repository.save(venue_provider)

    synchronize_venue_provider(venue_provider)
