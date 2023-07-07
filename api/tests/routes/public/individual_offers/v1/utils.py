from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories


ACCESSIBILITY_FIELDS = {
    "audioDisabilityCompliant": True,
    "mentalDisabilityCompliant": True,
    "motorDisabilityCompliant": True,
    "visualDisabilityCompliant": True,
}


def create_offerer_provider():
    offerer = offerers_factories.OffererFactory(name="Technical provider")
    provider = providers_factories.ProviderFactory(
        name="Technical provider", localClass=None, isActive=True, enabledForPro=True
    )
    api_key = offerers_factories.ApiKeyFactory(
        offerer=offerer,
        provider=provider,
    )
    providers_factories.OffererProviderFactory(
        offerer=offerer,
        provider=provider,
    )
    return provider, api_key


def create_offerer_provider_linked_to_venue(venue_params=None, is_virtual=False):
    venue_params = venue_params if venue_params else {}
    provider, api_key = create_offerer_provider()
    if is_virtual:
        venue = offerers_factories.VirtualVenueFactory(**venue_params)
    else:
        venue = offerers_factories.VenueFactory(**venue_params)
    providers_factories.VenueProviderFactory(venue=venue, provider=provider, venueIdAtOfferProvider="Test")
    return venue, api_key
