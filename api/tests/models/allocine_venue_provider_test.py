import pytest

from pcapi.core.offers.factories import VenueFactory
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import VenueProvider
from pcapi.model_creators.provider_creators import activate_provider


class AllocineVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_allocine_venue_provider_should_inherit_from_venue_provider(self, app):
        provider_allocine = activate_provider("AllocineStocks")
        providers_factories.AllocineVenueProviderFactory(provider=provider_allocine, isDuo=True)

        assert VenueProvider.query.count() == 1
        assert AllocineVenueProvider.query.count() == 1
        allocine_vp = VenueProvider.query.filter(VenueProvider.providerId == provider_allocine.id).first()
        assert isinstance(allocine_vp, AllocineVenueProvider)
        assert allocine_vp.isDuo
        assert allocine_vp.isFromAllocineProvider

    @pytest.mark.usefixtures("db_session")
    def test_query_venue_provider_load_allocine_venue_provider_attributes_when_connected_to_allocine(self, app):
        venue = VenueFactory()

        provider_allocine = providers_factories.AllocineProviderFactory()
        provider = providers_factories.ProviderFactory(localClass="TestLocalProvider")

        providers_factories.VenueProviderFactory(venue=venue, provider=provider)
        providers_factories.AllocineVenueProviderFactory(venue=venue, provider=provider_allocine, isDuo=True)

        assert VenueProvider.query.count() == 2
        assert AllocineVenueProvider.query.count() == 1
        created_venue_provider = VenueProvider.query.filter(VenueProvider.providerId == provider.id).first()
        assert isinstance(created_venue_provider, VenueProvider)

        created_allocine_venue_provider = VenueProvider.query.filter(
            VenueProvider.providerId == provider_allocine.id
        ).first()
        assert isinstance(created_allocine_venue_provider, AllocineVenueProvider)
