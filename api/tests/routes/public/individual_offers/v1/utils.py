from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories


ACCESSIBILITY_FIELDS = {
    "audioDisabilityCompliant": True,
    "mentalDisabilityCompliant": True,
    "motorDisabilityCompliant": True,
    "visualDisabilityCompliant": True,
}


def create_offerer_provider(with_charlie=False):
    booking_url = "http://example.com/booking" if with_charlie else None
    cancellation_url = "http://example.com/cancellation" if with_charlie else None
    offerer = offerers_factories.OffererFactory(name="Technical provider")
    provider = providers_factories.ProviderFactory(
        name="Technical provider",
        localClass=None,
        isActive=True,
        enabledForPro=True,
        bookingExternalUrl=booking_url,
        cancelExternalUrl=cancellation_url,
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


def create_offerer_provider_linked_to_venue(
    venue_params=None,
    is_virtual=False,
    with_charlie=False,
    is_venue_provider_active=True,
    venue_provider_permissions=None,
):
    venue_params = venue_params if venue_params else {}
    venue_provider_permissions = venue_provider_permissions or []
    provider, api_key = create_offerer_provider(with_charlie)
    if is_virtual:
        venue = offerers_factories.VirtualVenueFactory(**venue_params)
    else:
        venue = offerers_factories.VenueFactory(**venue_params)
    venue_provider = providers_factories.VenueProviderFactory(
        venue=venue, provider=provider, venueIdAtOfferProvider="Test", isActive=is_venue_provider_active
    )
    for permission_tuple in venue_provider_permissions:
        permission, resource = permission_tuple
        providers_factories.VenueProviderPermissionFactory(
            venueProvider=venue_provider, resource=resource, permission=permission
        )
    return venue, api_key
