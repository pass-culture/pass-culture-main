from pcapi.core.providers import models as providers_models

from . import exceptions


def check_ticketing_service_is_correctly_set(
    provider: providers_models.Provider, venue_provider: providers_models.VenueProvider | None
) -> None:
    if not (provider.hasProviderEnableCharlie or venue_provider and venue_provider.hasTicketingService):
        raise exceptions.ExternalBookingException("Ticketing system is not correctly set")
