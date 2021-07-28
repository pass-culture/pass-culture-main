import logging

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.models import db
from pcapi.repository import repository
from pcapi.workers.venue_provider_job import venue_provider_job


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


def _update_last_provider_id(venue: Venue, provider_id: int) -> None:
    """Update all offers' lastProviderId with the new provider_id."""
    query = """
      UPDATE "offer"
      SET "lastProviderId" = :provider_id
      WHERE
          offer."idAtProviders" IS NOT NULL
          AND offer."venueId" = :venue_id
    """
    db.session.execute(query, {"venue_id": venue.id, "provider_id": provider_id})
    db.session.commit()


def fully_sync_venue(venue: Venue) -> None:
    logger.info("Resetting all stock quantity for full resync", extra={"venue": venue.id})
    _reset_stock_quantity(venue)

    venue_provider = VenueProvider.query.filter_by(venueId=venue.id, isActive=True).one()
    venue_provider.lastSyncDate = None
    repository.save(venue_provider)

    synchronize_venue_provider(venue_provider)


def fully_sync_venue_with_new_provider(venue: Venue, provider_id: int) -> None:
    logger.info("Resetting all stock quantity for changed sync", extra={"venue": venue.id})
    _reset_stock_quantity(venue)

    venue_provider = VenueProvider.query.filter_by(venueId=venue.id).one()
    venue_provider.lastSyncDate = None
    venue_provider.providerId = provider_id
    logger.info(
        "Changing venue_provider.provider_id", extra={"venue_provider": venue_provider.id, "provider": provider_id}
    )
    repository.save(venue_provider)

    logger.info("Updating offer.last_provider_id for changed sync", extra={"venue": venue.id, "provider": provider_id})
    _update_last_provider_id(venue, provider_id)

    venue_provider_job.delay(venue_provider.id)
