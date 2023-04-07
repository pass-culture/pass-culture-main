import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.providers import factories
from pcapi.core.providers import models
from pcapi.core.providers import repository


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_venue_provider_by_id_regular_venue_provider():
    provider = factories.VenueProviderFactory()
    assert repository.get_venue_provider_by_id(provider.id) == provider


def test_get_venue_provider_by_id_allocine_venue_provider():
    provider = factories.AllocineVenueProviderFactory()
    assert repository.get_venue_provider_by_id(provider.id) == provider


def test_get_active_venue_providers_by_provider():
    provider = factories.ProviderFactory()
    vp1 = factories.VenueProviderFactory(provider=provider, isActive=True)
    factories.VenueProviderFactory(provider=provider, isActive=False)
    factories.VenueProviderFactory()

    assert repository.get_active_venue_providers_by_provider(provider.id) == [vp1]


class GetAvailableProvidersTest:
    def _clean(self):
        # Remove providers that are automatically added for all tests,
        # so that our tests here start with an empty "provider" table.
        models.Provider.query.delete()

    def test_basics(self):
        self._clean()
        provider = factories.APIProviderFactory(name="Other")
        _provider_allocine = factories.AllocineProviderFactory(name="Allociné")
        _not_active = factories.APIProviderFactory(isActive=False)
        _not_enabled_for_pro = factories.APIProviderFactory(enabledForPro=False)

        venue = offerers_factories.VenueFactory()

        providers = list(repository.get_available_providers(venue))
        assert providers == [provider]

    def test_allocine(self):
        self._clean()
        provider_allocine = factories.AllocineProviderFactory(name="Allociné")
        provider_other = factories.APIProviderFactory(name="Other")

        venue = offerers_factories.VenueFactory()
        factories.AllocineTheaterFactory(siret=venue.siret)

        providers = list(repository.get_available_providers(venue))
        assert providers == [provider_allocine, provider_other]

    def test_cinema_providers(self):
        self._clean()
        provider_other = factories.APIProviderFactory(name="Other")
        provider_cds = factories.ProviderFactory(name="CDS", localClass="CDSStocks")
        venue = offerers_factories.VenueFactory()
        factories.CinemaProviderPivotFactory(venue=venue, provider=provider_cds)

        providers = list(repository.get_available_providers(venue))
        assert providers == [provider_cds, provider_other]
