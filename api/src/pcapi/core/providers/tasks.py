import logging
import time

from pcapi import settings
from pcapi.local_providers import provider_manager
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task

from . import models


logger = logging.getLogger(__name__)


class SynchronizeVenueProvidersRequest(BaseModel):
    venue_provider_ids: list[int]


@task(settings.GCP_SYNCHRONIZE_VENUE_PROVIDERS_QUEUE_NAME, "/providers/synchronize_venue_providers")  # type: ignore [arg-type]
def synchronize_venue_providers_task(payload: SynchronizeVenueProvidersRequest) -> None:
    start_timer = time.perf_counter()

    venue_providers = models.VenueProvider.query.filter(models.VenueProvider.id.in_(payload.venue_provider_ids)).all()
    provider_manager.synchronize_venue_providers(venue_providers)

    duration = time.perf_counter() - start_timer

    if duration >= 0.5 * 60 * 60:  # 50% of time between two ProviderAPIsSync cron jobs
        provider = venue_providers[0].provider
        logger.error("Synchronization with provider=%s took a long time", provider.name, extra={"duration": duration})
