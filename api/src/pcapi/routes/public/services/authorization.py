import logging

from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.models import api_errors
from pcapi.validation.routes.users_authentifications import current_api_key


logger = logging.getLogger(__name__)


def get_venue_provider_or_raise_404(venue_id: int) -> providers_models.VenueProvider:
    """
    Return active `VenueProvider` linking the venue to the current provider

    Raise `ResourceNotFoundError` if no active `VenueProvider` is found because it means
    provider should have access to the venue.
    """
    venue_provider = providers_repository.get_venue_provider_by_venue_and_provider_ids(
        venue_id=venue_id, provider_id=current_api_key.providerId
    )

    if not venue_provider or not venue_provider.isActive:
        raise api_errors.ResourceNotFoundError(errors={"global": "Venue cannot be found"})

    return venue_provider
