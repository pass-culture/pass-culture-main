import pytest
from flask import g

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.models import api_errors
from pcapi.routes.public.services import authorization


@pytest.mark.usefixtures("db_session")
class GetVenueProviderOrRaise404Test:
    def setup_current_provider(self):
        provider = providers_factories.ProviderFactory()
        g.current_api_key = offerers_factories.ApiKeyFactory(provider=provider)
        return provider

    def test_should_return_the_venue_provider_linking_the_venue_to_the_current_provider(self):
        venue = offerers_factories.VenueFactory()
        provider = self.setup_current_provider()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)

        assert authorization.get_venue_provider_or_raise_404(venue_id=venue.id) == venue_provider

    def test_should_raise_a_404_when_the_venue_is_not_linked_to_the_current_provider(self):
        venue = offerers_factories.VenueFactory()
        self.setup_current_provider()

        with pytest.raises(api_errors.ResourceNotFoundError) as exc_info:
            authorization.get_venue_provider_or_raise_404(venue_id=venue.id)

        assert exc_info.value.errors == {"global": "Venue cannot be found"}
        assert exc_info.value.status_code == 404

    def test_should_raise_a_404_when_the_venue_provider_is_not_active(self):
        venue = offerers_factories.VenueFactory()
        provider = self.setup_current_provider()
        providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=False)

        with pytest.raises(api_errors.ResourceNotFoundError) as exc_info:
            authorization.get_venue_provider_or_raise_404(venue_id=venue.id)

        assert exc_info.value.errors == {"global": "Venue cannot be found"}
