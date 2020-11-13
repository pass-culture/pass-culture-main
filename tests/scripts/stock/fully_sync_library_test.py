from unittest.mock import patch

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.repository import repository
from pcapi.scripts.stock.fully_sync_library import fully_sync_library


class FullySyncLibraryTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.scripts.stock.fully_sync_library.do_sync_venue_provider")
    def should_call_synchronize_on_expected_venue_provider(self, mock_do_sync_venue_provider, app):
        # Given
        venue = VenueFactory()
        offer = OfferFactory(venue=venue)
        stock = StockFactory(offer=offer)
        titelive = activate_provider(provider_classname="TiteLiveStocks")
        venue_provider = create_venue_provider(venue=venue, provider=titelive)

        repository.save(venue_provider, stock)

        # When
        fully_sync_library(venue_id=venue.id)

        # Then
        mock_do_sync_venue_provider.assert_called_once_with(venue_provider)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.scripts.stock.fully_sync_library.do_sync_venue_provider")
    def should_update_quantity_to_booking_amount_for_each_synchronized_stock_on_venue(
        self, mock_do_sync_venue_provider, app
    ):
        # Given
        titelive = activate_provider(provider_classname="TiteLiveStocks")
        venue = VenueFactory()
        offer = OfferFactory(venue=venue, idAtProviders="titelive")
        stock = StockFactory(offer=offer, quantity=2, lastProviderId=titelive.id, idAtProviders="titelive")
        booking = BookingFactory(stock=stock)
        venue_provider = create_venue_provider(venue=venue, provider=titelive)

        repository.save(venue_provider, booking)

        # When
        fully_sync_library(venue_id=venue.id)

        # Then
        assert stock.quantity == 1
