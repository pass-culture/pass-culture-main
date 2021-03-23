import logging
from time import sleep

from pcapi import settings
from pcapi.connectors.scalingo_api import ScalingoApiException
from pcapi.connectors.scalingo_api import run_process_in_one_off_container
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.models import VenueProvider
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository.venue_provider_queries import get_active_venue_providers_for_specific_provider
from pcapi.repository.venue_provider_queries import get_nb_containers_at_work
from pcapi.repository.venue_provider_queries import get_venue_providers_to_sync


logger = logging.getLogger(__name__)


WAIT_TIME_FOR_AVAILABLE_WORKER = 60

# FIXME (dbaty, 2021-02-05): if the new simplified implementation
# stays, we can clean up a few things:
# - remove the feature flag
# - remove `VenueProvider.syncWorkerId`
# - remove `get_venue_providers_to_sync()`
# - inline this function into `synchronize_titelive_stocks()`?
def update_venues_for_specific_provider(provider_id: int):
    if feature_queries.is_active(FeatureToggle.PARALLEL_SYNCHRONIZATION_OF_VENUE_PROVIDER):
        _update_venues_in_parallel(provider_id)
        return

    venue_providers_to_sync = get_active_venue_providers_for_specific_provider(provider_id)
    for venue_provider in venue_providers_to_sync:
        synchronize_venue_provider(venue_provider)


def _update_venues_in_parallel(provider_id: int):
    venue_providers_to_sync = get_venue_providers_to_sync(provider_id)
    sync_worker_pool = settings.PROVIDERS_SYNC_WORKERS_POOL_SIZE
    while len(venue_providers_to_sync) > 0:
        venue_provider = venue_providers_to_sync[0]
        has_remaining_slot_in_pool = sync_worker_pool - get_nb_containers_at_work() > 0
        if has_remaining_slot_in_pool:
            do_sync_venue_provider(venue_provider)
            venue_providers_to_sync.remove(venue_provider)
        else:
            sleep(WAIT_TIME_FOR_AVAILABLE_WORKER)


def do_sync_venue_provider(venue_provider: VenueProvider):
    update_venue_provider_command = (
        f"python src/pcapi/scripts/pc.py update_providables" f" --venue-provider-id {venue_provider.id}"
    )
    try:
        container_id = run_process_in_one_off_container(update_venue_provider_command)
        venue_provider.syncWorkerId = container_id
        repository.save(venue_provider)
        logger.info(
            "[VenueProviderWorker] VenueProvider %s synchro in container %s",
            venue_provider.venueIdAtOfferProvider,
            container_id,
        )
    except ScalingoApiException as error:
        logger.exception(
            "[VenueProviderWorker] Error synchronizing VenueProvider %s with errors: %s",
            venue_provider.venueIdAtOfferProvider,
            error,
        )
