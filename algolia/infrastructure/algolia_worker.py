import os
from time import sleep
from typing import Dict

from redis import Redis

from connectors.redis import get_venue_providers
from connectors.scalingo_api import run_process_in_one_off_container, ScalingoApiException
from utils.logger import logger

WAIT_TIME_FOR_AVAILABLE_WORKER = 60
DEFAULT_SYNC_WORKERS_POOL_SIZE = 10


def process_multi_indexing(client: Redis):
    venue_providers_to_process = get_venue_providers(client=client)
    sync_worker_pool = int(os.environ.get('SYNC_WORKERS_POOL_SIZE', DEFAULT_SYNC_WORKERS_POOL_SIZE))

    counter = 0
    while len(venue_providers_to_process) > 0:
        venue_provider = venue_providers_to_process[0]
        has_remaining_slot_in_pool = sync_worker_pool - counter > 0

        if has_remaining_slot_in_pool:
            _run_indexing(venue_provider=venue_provider)
            venue_providers_to_process.pop(0)
            counter += 1
        else:
            sleep(WAIT_TIME_FOR_AVAILABLE_WORKER)
            counter = 0


def _run_indexing(venue_provider: Dict):
    venue_provider_id = venue_provider['id']
    provider_id = venue_provider['providerId']
    venue_id = venue_provider['venueId']

    run_algolia_venue_provider_command = f"PYTHONPATH=. " \
                                         f"python scripts/pc.py run_algolia_venue_provider " \
                                         f"--provider-id {provider_id} " \
                                         f"--venueId {venue_id} "
    try:
        container_id = run_process_in_one_off_container(run_algolia_venue_provider_command)
        logger.info(f"[ALGOLIA][VenueProviderWorker] Indexing offers from VenueProvider {venue_provider_id}"
                    f" synchro in container {container_id}")
    except ScalingoApiException as error:
        logger.error(f"[ALGOLIA][VenueProviderWorker] Error indexing offers from VenueProvider {venue_provider_id}"
                     f" with errors: {error}")
