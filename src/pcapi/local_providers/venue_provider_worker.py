from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.repository.venue_provider_queries import get_active_venue_providers_for_specific_provider


def update_venues_for_specific_provider(provider_id: int):
    venue_providers_to_sync = get_active_venue_providers_for_specific_provider(provider_id)
    for venue_provider in venue_providers_to_sync:
        synchronize_venue_provider(venue_provider)
