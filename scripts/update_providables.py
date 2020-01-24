from flask import current_app as app

from local_providers.provider_manager import do_update, get_local_provider_class_by_name
from models import VenueProvider


@app.manager.option('-p',
                    '--provider-name',
                    help='Limit update to this provider name')
@app.manager.option('-l',
                    '--limit',
                    help='Limit update to n items per providerName/venueId'
                         + ' (for test purposes)', type=int)
@app.manager.option('-w',
                    '--venue-provider-id',
                    help='Limit update to this venue provider id')
def update_providables(provider_name: str, venue_provider_id: str, limit: int):
    if (provider_name and venue_provider_id) or not (provider_name or venue_provider_id):
        raise ValueError('Call either with provider-name or venue-provider-id')

    if provider_name:
        ProviderClass = get_local_provider_class_by_name(provider_name)
        provider = ProviderClass()
        return do_update(provider, limit)

    if venue_provider_id:
        venue_provider = VenueProvider.query.get(venue_provider_id)
        ProviderClass = get_local_provider_class_by_name(venue_provider.provider.localClass)
        provider = ProviderClass(venue_provider)
        return do_update(provider, limit)


@app.manager.option('-p',
                    '--provider-id',
                    help='Update providables for this provider')
@app.manager.option('-l',
                    '--limit',
                    help='Limit update to n items per venue provider'
                         + ' (for test purposes)', type=int)
def update_providables_by_provider_id(provider_id: str, limit: int):
    provider_id = int(provider_id)
    venue_providers = VenueProvider.query.filter(VenueProvider.providerId == provider_id).all()
    for venue_provider in venue_providers:
        ProviderClass = get_local_provider_class_by_name(venue_provider.provider.localClass)
        provider = ProviderClass(venue_provider)
        do_update(provider, limit)
    pass
