from pcapi import settings
from pcapi.local_providers import provider_manager
from pcapi.tasks.decorator import task

from . import models


@task(settings.GCP_SYNCHRONIZE_VENUE_PROVIDERS_QUEUE_NAME, "/providers/synchronize_venue_providers")  # type: ignore [arg-type]
def synchronize_venue_providers_task(venue_provider_ids: list[int]) -> None:
    venue_providers = models.VenueProvider.query.filter(models.VenueProvider.id.in_(venue_provider_ids)).all()
    provider_manager.synchronize_venue_providers(venue_providers)
