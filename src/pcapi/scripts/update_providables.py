from flask import current_app as app

from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.repository.venue_provider_queries import get_venue_provider_by_id


@app.manager.option("-p", "--provider-name", help="Limit update to this provider name")
@app.manager.option(
    "-l", "--limit", help="Limit update to n items per providerName/venueId" + " (for test purposes)", type=int
)
@app.manager.option("-w", "--venue-provider-id", help="Limit update to this venue provider id")
def update_providables(provider_name: str, venue_provider_id: str, limit: int):
    if (provider_name and venue_provider_id) or not (provider_name or venue_provider_id):
        raise ValueError("Call either with provider-name or venue-provider-id")

    if provider_name:
        synchronize_data_for_provider(provider_name, limit)

    if venue_provider_id:
        venue_provider = get_venue_provider_by_id(int(venue_provider_id))
        synchronize_venue_provider(venue_provider, limit)


@app.manager.option("-p", "--provider-id", help="Update providables for this provider")
@app.manager.option(
    "-l", "--limit", help="Limit update to n items per venue provider" + " (for test purposes)", type=int
)
def update_providables_by_provider_id(provider_id: str, limit: int):
    synchronize_venue_providers_for_provider(limit, int(provider_id))
