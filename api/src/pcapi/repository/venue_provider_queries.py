from pcapi.core.providers.models import VenueProvider


def get_active_venue_providers_for_specific_provider(provider_id: int) -> list[VenueProvider]:
    return (
        VenueProvider.query.filter(VenueProvider.providerId == provider_id).filter(VenueProvider.isActive == True).all()
    )

    return VenueProvider.query.get(venue_provider_id)
