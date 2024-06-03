import logging
import time

from pcapi import settings
from pcapi.local_providers import provider_manager
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task

from . import models


logger = logging.getLogger(__name__)


class SynchronizeVenueProvidersRequest(BaseModel):
    provider_id: int
    venue_provider_ids: list[int]


@task(settings.GCP_SYNCHRONIZE_VENUE_PROVIDERS_QUEUE_NAME, "/providers/synchronize_venue_providers", task_request_timeout=30 * 60)  # type: ignore[arg-type]
def synchronize_venue_providers_task(payload: SynchronizeVenueProvidersRequest) -> None:
    provider_id = payload.provider_id
    venue_provider_ids = payload.venue_provider_ids
    venue_providers = models.VenueProvider.query.filter(models.VenueProvider.id.in_(venue_provider_ids)).all()

    if not venue_providers:
        return

    start_timer = time.perf_counter()
    logger.info(
        "Synchronization job started",
        extra={
            "providerid": provider_id,
            "venue_providers": venue_provider_ids,
        },
    )

    provider_manager.synchronize_venue_providers(venue_providers)

    duration = time.perf_counter() - start_timer
    if duration >= 0.5 * 60 * 60:  # 50% of time between two ProviderAPIsSync cron jobs
        logger.error(
            "Synchronization of venue providers took a long time",
            extra={
                "provider": provider_id,
                "duration": duration,
                "venue_providers": venue_provider_ids,
            },
        )

    logger.info(
        "Synchronization with provider finished",
        extra={
            "provider": provider_id,
            "duration": duration,
        },
    )
