from connectors.scalingo_api import run_process_in_one_off_container, ScalingoApiException
from models import VenueProvider, PcObject
from repository.venue_provider_queries import get_venue_providers_to_sync
from utils.logger import logger


def update_venues_for_specific_provider(provider_id: int):
    venue_providers_to_sync = get_venue_providers_to_sync(provider_id)

    for venue_provider in venue_providers_to_sync:
        do_sync_venue_provider(venue_provider)


def do_sync_venue_provider(venue_provider: VenueProvider):
    update_venue_provider_command = f"PYTHONPATH=. python scripts/pc.py update_providables" \
                                    f" --venue-provider-id {venue_provider.id}"
    try:
        container_id = run_process_in_one_off_container(update_venue_provider_command)
        venue_provider.syncWorkerId = container_id
        PcObject.save(venue_provider)
        logger.info(f"[VenueProviderWorker] VenueProvider {venue_provider.venueIdAtOfferProvider}"
                    f" synchro in container {container_id}")
    except ScalingoApiException as error:
        logger.error(f"[VenueProviderWorker] Error synchronizing VenueProvider {venue_provider.venueIdAtOfferProvider}"
                     f" with errors: {error}")
