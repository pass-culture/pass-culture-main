import pcapi.core.providers.repository as providers_repository
from pcapi.local_providers.provider_manager import synchronize_ems_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def venue_provider_job(venue_provider_id: int) -> None:
    venue_provider = providers_repository.get_venue_provider_by_id(venue_provider_id)
    if venue_provider.provider.localClass == "EMSStocks":
        synchronize_ems_venue_provider(venue_provider)
    else:
        synchronize_venue_provider(venue_provider)
