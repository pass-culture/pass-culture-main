import pytest

from pcapi.core.external_bookings import exceptions as external_bookings_exceptions
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
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


class IsEventExternalTicketApplicableTest:
    def test_external_ticket_applicable(self):
        provider = factories.PublicApiProviderFactory(name="Music party")
        offer = offers_factories.EventOfferFactory(
            lastProvider=provider, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        assert repository.is_event_external_ticket_applicable(offer) is True

    def test_external_ticket_not_applicable_if_offer_not_event(self):
        provider = factories.PublicApiProviderFactory(name="Music party", isActive=False)
        offer = offers_factories.OfferFactory(lastProvider=provider)
        assert repository.is_event_external_ticket_applicable(offer) is False

    def test_external_not_applicable_if_offer_not_in_app(self):
        provider = factories.PublicApiProviderFactory(name="Music party")
        offer = offers_factories.EventOfferFactory(lastProvider=provider)
        assert repository.is_event_external_ticket_applicable(offer) is False

    def test_raises_error_if_offer_in_app_and_provider_inactive(self):
        provider = factories.PublicApiProviderFactory(name="Music party", isActive=False)
        offer = offers_factories.EventOfferFactory(
            lastProvider=provider, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        with pytest.raises(external_bookings_exceptions.ExternalBookingException):
            repository.is_event_external_ticket_applicable(offer)

    def test_raises_error_if_offer_in_app_and_provider_has_not_enabled_charlie(self):
        provider = factories.PublicApiProviderFactory(name="Music party", bookingExternalUrl=None)
        offer = offers_factories.EventOfferFactory(
            lastProvider=provider, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        with pytest.raises(external_bookings_exceptions.ExternalBookingException):
            repository.is_event_external_ticket_applicable(offer)


def test_get_allocine_theater():
    venue_with_theater = offerers_factories.VenueFactory()
    theater = factories.AllocineTheaterFactory(siret=venue_with_theater.siret)
    assert repository.get_allocine_theater(venue_with_theater) == theater

    venue_without_theater = offerers_factories.VenueFactory()
    assert repository.get_allocine_theater(venue_without_theater) is None
