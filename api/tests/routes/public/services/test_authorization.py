from flask import g
import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.models import api_errors
from pcapi.routes.public.services import authorization


@pytest.mark.usefixtures("db_session")
class GetVenueProviderOrRaise404Test:

    def should_raise_resource_not_found_error_when_no_venue_provider(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.ProviderFactory()
        api_key = offerers_factories.ApiKeyFactory(provider=provider)
        g.current_api_key = api_key

        with pytest.raises(api_errors.ResourceNotFoundError) as exc_info:
            authorization.get_venue_provider_or_raise_404(venue_id=venue.id)

        assert exc_info.value.errors == {"global": "Venue cannot be found"}

    def should_raise_resource_not_found_error_when_venue_provider_is_not_active(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.ProviderFactory()
        providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=False)
        api_key = offerers_factories.ApiKeyFactory(provider=provider)
        g.current_api_key = api_key

        with pytest.raises(api_errors.ResourceNotFoundError) as exc_info:
            authorization.get_venue_provider_or_raise_404(venue_id=venue.id)

        assert exc_info.value.errors == {"global": "Venue cannot be found"}
