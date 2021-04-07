import subprocess

from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_provider_enabled_for_pro_by_id
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository.venue_queries import find_by_id
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.use_cases.connect_venue_to_allocine import connect_venue_to_allocine
from pcapi.use_cases.connect_venue_to_provider import connect_venue_to_provider
from pcapi.utils.human_ids import dehumanize
from pcapi.validation.routes.venue_providers import check_existing_provider
from pcapi.validation.routes.venues import check_existing_venue
from pcapi.workers.venue_provider_job import venue_provider_job


def create_venue_provider(venue_provider: PostVenueProviderBody) -> VenueProvider:
    provider_id = dehumanize(venue_provider.providerId)
    provider = get_provider_enabled_for_pro_by_id(provider_id)
    check_existing_provider(provider)

    venue_id = dehumanize(venue_provider.venueId)
    venue = find_by_id(venue_id)
    check_existing_venue(venue)

    if provider.localClass == "AllocineStocks":
        new_venue_provider = connect_venue_to_allocine(venue, venue_provider)
    else:
        new_venue_provider = connect_venue_to_provider(venue, provider)

    _run_first_synchronization(new_venue_provider)

    return new_venue_provider


def _run_first_synchronization(new_venue_provider: VenueProvider) -> None:
    if not feature_queries.is_active(FeatureToggle.SYNCHRONIZE_VENUE_PROVIDER_IN_WORKER):
        subprocess.Popen(
            [
                "python",
                "src/pcapi/scripts/pc.py",
                "update_providables",
                "--venue-provider-id",
                str(new_venue_provider.id),
            ]
        )
        return

    venue_provider_job.delay(new_venue_provider.id)
