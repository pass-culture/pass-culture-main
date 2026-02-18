from pydantic import BaseModel as BaseModelV2

import pcapi.core.providers.repository as providers_repository
from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.local_providers.provider_manager import synchronize_ems_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_provider


class CinemaSynchronisationTaskPayload(BaseModelV2):
    venue_provider_id: int


@celery_async_task(
    name="tasks.providers.default.synchronize_cinema_sessions",
    model=CinemaSynchronisationTaskPayload,
)
def synchronize_cinema_sessions_task(payload: CinemaSynchronisationTaskPayload) -> None:
    venue_provider = providers_repository.get_venue_provider_by_id(payload.venue_provider_id)
    if venue_provider.provider.localClass == "EMSStocks":
        synchronize_ems_venue_provider(venue_provider)
    else:
        synchronize_venue_provider(venue_provider)
