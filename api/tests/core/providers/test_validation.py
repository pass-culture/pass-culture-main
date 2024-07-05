import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.providers import exceptions
from pcapi.core.providers import factories
from pcapi.core.providers import validation


pytestmark = pytest.mark.usefixtures("db_session")


class CheckTicketingUrlsAreCoherentlySetTest:

    def test_should_raise(self):
        with pytest.raises(exceptions.TicketingUrlsMustBeBothSet):
            validation.check_ticketing_urls_are_coherently_set("https://coucou.com", None)

        with pytest.raises(exceptions.TicketingUrlsMustBeBothSet):
            validation.check_ticketing_urls_are_coherently_set(None, "https://aurevoir.com")

    def test_should_not_raise(self):
        validation.check_ticketing_urls_are_coherently_set("https://coucou.com", "https://aurevoir.com")
        validation.check_ticketing_urls_are_coherently_set(None, None)


class CheckTicketingUrlsCanBeUnsetTest:

    def test_should_raise(self):
        provider = factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        factories.VenueProviderFactory(provider=provider, venue=venue)
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        offers_factories.StockFactory(offer=event_offer)

        with pytest.raises(exceptions.TicketingUrlsCannotBeUnset) as e:
            validation.check_ticketing_urls_can_be_unset(provider)

        assert e.value.blocking_events_ids == [event_offer.id]

    def test_should_not_raise(self):
        provider = factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        factories.VenueProviderFactory(provider=provider, venue=venue)
        offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )

        validation.check_ticketing_urls_can_be_unset(provider)


class CheckVenueTicketingUrlsCanBeUnsetTest:

    def test_should_raise(self):
        provider_without_ticketing_urls = factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = factories.VenueProviderFactory(provider=provider_without_ticketing_urls, venue=venue)
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider_without_ticketing_urls,
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        offers_factories.StockFactory(offer=event_offer)

        with pytest.raises(exceptions.TicketingUrlsCannotBeUnset) as e:
            validation.check_venue_ticketing_urls_can_be_unset(venue_provider)

        assert e.value.blocking_events_ids == [event_offer.id]

    def test_should_not_raise_because_provider_has_ticketing_urls(self):
        provider_with_ticketing_urls = factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = factories.VenueProviderFactory(provider=provider_with_ticketing_urls, venue=venue)
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider_with_ticketing_urls,
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        offers_factories.StockFactory(offer=event_offer)

        validation.check_venue_ticketing_urls_can_be_unset(venue_provider)

    def test_should_not_raise_because_there_is_no_future_stock(self):
        provider_without_ticketing_urls = factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = factories.VenueProviderFactory(provider=provider_without_ticketing_urls, venue=venue)
        offers_factories.EventOfferFactory(
            lastProvider=provider_without_ticketing_urls,
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )

        validation.check_venue_ticketing_urls_can_be_unset(venue_provider)
