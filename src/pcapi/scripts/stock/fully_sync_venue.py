import logging

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.api import reset_stock_quantity
from pcapi.core.providers.api import update_last_provider_id
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.repository import repository
from pcapi.workers.venue_provider_job import venue_provider_job


logger = logging.getLogger(__name__)


def fully_sync_venue(venue: Venue) -> None:
    logger.info("Resetting all stock quantity for full resync", extra={"venue": venue.id})
    reset_stock_quantity(venue)

    venue_provider = VenueProvider.query.filter_by(venueId=venue.id, isActive=True).one()
    venue_provider.lastSyncDate = None
    repository.save(venue_provider)

    synchronize_venue_provider(venue_provider)


def fully_sync_venue_with_new_provider(venue: Venue, provider_id: int) -> None:
    logger.info("Resetting all stock quantity for changed sync", extra={"venue": venue.id})
    reset_stock_quantity(venue)

    venue_provider = VenueProvider.query.filter_by(venueId=venue.id).one()
    venue_provider.lastSyncDate = None
    venue_provider.providerId = provider_id
    logger.info(
        "Changing venue_provider.provider_id", extra={"venue_provider": venue_provider.id, "provider": provider_id}
    )
    repository.save(venue_provider)

    logger.info("Updating offer.last_provider_id for changed sync", extra={"venue": venue.id, "provider": provider_id})
    update_last_provider_id(venue, provider_id)

    venue_provider_job.delay(venue_provider.id)
