from datetime import datetime
from datetime import timedelta

import pytest

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


def test_get_allocine_theater():
    venue_with_theater = offerers_factories.VenueFactory()
    theater = factories.AllocineTheaterFactory(siret=venue_with_theater.siret)
    assert repository.get_allocine_theater(venue_with_theater) == theater

    venue_without_theater = offerers_factories.VenueFactory()
    assert repository.get_allocine_theater(venue_without_theater) is None


class GetFutureEventsRequiringProviderTicketingSystemTest:

    def test_should_return_a_one_event_list(self):
        provider = factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        factories.VenueProviderFactory(provider=provider, venue=venue)

        expected_event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        # event not linked to ticketing
        offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL
        )
        # event with no stock
        offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )

        offers_factories.StockFactory(offer=expected_event_offer)

        future_events = repository.get_future_events_requiring_provider_ticketing_system(provider)

        assert len(future_events) == 1
        assert future_events[0] == expected_event_offer

    def test_should_return_no_event_because_there_is_a_venue_booking_url(self):
        provider = factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = factories.VenueProviderFactory(provider=provider, venue=venue)
        # External URLS defined at Venue level
        factories.VenueProviderExternalUrlsFactory(venueProvider=venue_provider)
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        offers_factories.StockFactory(offer=event_offer)

        future_events = repository.get_future_events_requiring_provider_ticketing_system(provider)

        assert len(future_events) == 0

    def test_should_return_no_event_because_stock_is_in_the_past(self):
        provider = factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        factories.VenueProviderFactory(provider=provider, venue=venue)
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        # Old stock
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        offers_factories.StockFactory(offer=event_offer, beginningDatetime=one_day_ago)

        future_events = repository.get_future_events_requiring_provider_ticketing_system(provider)

        assert len(future_events) == 0


class GetFutureVenueEventsRequiringATicketingSystemTest:

    def test_should_return_a_one_event_list(self):
        provider = factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_2 = offerers_factories.VenueFactory()
        venue_provider = factories.VenueProviderFactory(provider=provider, venue=venue)

        expected_event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )

        # event with old stock
        event_with_old_sock = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        # event not linked to ticketing
        not_linked_to_ticketing_event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.BY_EMAIL
        )
        # event with no stock
        offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )

        # event linked to other venue
        linked_to_other_venue_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue_2, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )

        offers_factories.StockFactory(offer=expected_event_offer)
        offers_factories.StockFactory(offer=not_linked_to_ticketing_event_offer)
        offers_factories.StockFactory(offer=linked_to_other_venue_offer)
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        offers_factories.StockFactory(offer=event_with_old_sock, beginningDatetime=one_day_ago)

        future_events = repository.get_future_venue_events_requiring_a_ticketing_system(venue_provider)

        assert len(future_events) == 1
        assert future_events[0] == expected_event_offer
