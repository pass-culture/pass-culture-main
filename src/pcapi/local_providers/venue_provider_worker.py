import os
from time import sleep

from pcapi.connectors.scalingo_api import ScalingoApiException
from pcapi.connectors.scalingo_api import run_process_in_one_off_container
from pcapi.models import VenueProvider
from pcapi.repository import repository
from pcapi.repository.venue_provider_queries import get_nb_containers_at_work
from pcapi.repository.venue_provider_queries import get_venue_providers_to_sync
from pcapi.utils.logger import logger


WAIT_TIME_FOR_AVAILABLE_WORKER = 60
DEFAULT_WORKERS_POOL_SIZE = 5


def update_venues_for_specific_provider(provider_id: int):
    venue_providers_to_sync = get_venue_providers_to_sync(provider_id)
    sync_worker_pool = int(os.environ.get('SYNC_WORKERS_POOL_SIZE', DEFAULT_WORKERS_POOL_SIZE))
    while len(venue_providers_to_sync) > 0:
        venue_provider = venue_providers_to_sync[0]
        has_remaining_slot_in_pool = sync_worker_pool - get_nb_containers_at_work() > 0
        if has_remaining_slot_in_pool:
            do_sync_venue_provider(venue_provider)
            venue_providers_to_sync.remove(venue_provider)
        else:
            sleep(WAIT_TIME_FOR_AVAILABLE_WORKER)


def do_sync_venue_provider(venue_provider: VenueProvider):
    update_venue_provider_command = f"python src/pcapi/scripts/pc.py update_providables" \
                                    f" --venue-provider-id {venue_provider.id}"
    try:
        container_id = run_process_in_one_off_container(update_venue_provider_command)
        venue_provider.syncWorkerId = container_id
        repository.save(venue_provider)
        logger.info(f"[VenueProviderWorker] VenueProvider {venue_provider.venueIdAtOfferProvider}"
                    f" synchro in container {container_id}")
    except ScalingoApiException as error:
        logger.exception(f"[VenueProviderWorker] Error synchronizing VenueProvider {venue_provider.venueIdAtOfferProvider}"
                     f" with errors: {error}")
