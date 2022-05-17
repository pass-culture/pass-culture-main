from unittest.mock import patch

import pytest

from pcapi.core.booking_providers.factories import VenueBookingProviderFactory
from pcapi.core.booking_providers.models import Movie
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.local_providers.booking_providers.cds.cds_stocks import CDSStocks
from pcapi.models.product import Product

from tests.conftest import clean_database


@pytest.mark.usefixtures("db_session")
class CDSStocksTest:
    @clean_database
    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    def should_get_venue_movies(self, mock_get_venue_movies):

        # Given
        venue_booking_provider = VenueBookingProviderFactory()
        mocked_movies = [
            Movie(id="1", title="movieTest", duration=120, description="testDescription", visa="123456"),
            Movie(id="2", title="movieTest 2", duration=120, description="ceci est un film", visa="111111"),
        ]
        mock_get_venue_movies.return_value = mocked_movies

        # When
        cds_stocks = CDSStocks(venue_provider=venue_booking_provider)
        cds_movies = list(cds_stocks.movies)

        # Then
        mock_get_venue_movies.assert_called_once()
        assert len(cds_movies) == 2

    @clean_database
    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    def should_return_providable_info_on_next(self, mock_get_venue_movies):
        # Given
        venue_booking_provider = VenueBookingProviderFactory()
        mocked_movies = [
            Movie(id="1", title="movieTest", duration=120, description="testDescription", visa="123456"),
        ]
        mock_get_venue_movies.return_value = mocked_movies

        # When
        cds_stocks = CDSStocks(venue_provider=venue_booking_provider)
        providable_infos = next(cds_stocks)

        # Then
        assert len(providable_infos) == 2

        product_providable_info = providable_infos[0]
        offer_providable_info = providable_infos[1]

        assert product_providable_info.type == Product
        assert product_providable_info.id_at_providers == "1"
        assert product_providable_info.new_id_at_provider == "1"

        assert offer_providable_info.type == Offer
        assert offer_providable_info.id_at_providers == "1"
        assert offer_providable_info.new_id_at_provider == "1"

    @clean_database
    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    def should_create_offers_for_each_movies(self, mock_get_venue_movies):
        # Given
        venue_booking_provider = VenueBookingProviderFactory(provider__localClass="CDSStocks", isDuo=True)
        mocked_movies = [
            Movie(id="1", title="movieTest", duration=120, description="testDescription", visa="123456"),
            Movie(id="2", title="movieTest 2", duration=120, description="ceci est un film", visa="111111"),
        ]
        mock_get_venue_movies.return_value = mocked_movies
        cds_stocks = CDSStocks(venue_provider=venue_booking_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offer = Offer.query.all()
        created_product = Product.query.all()

        assert len(created_offer) == 2
        assert len(created_product) == 2

    @clean_database
    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    def should_fill_offer_and_product_informations_for_each_movies(self, mock_get_venue_movies):
        # Given
        venue_booking_provider = VenueBookingProviderFactory(provider__localClass="CDSStocks", isDuo=True)
        mocked_movies = [
            Movie(id="1", title="movieTest", duration=120, description="testDescription", visa="123456"),
        ]
        mock_get_venue_movies.return_value = mocked_movies
        cds_stocks = CDSStocks(venue_provider=venue_booking_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offer = Offer.query.one()
        created_product = Product.query.one()

        assert created_offer.name == "movieTest"
        assert created_offer.product == created_product
        assert created_offer.venue == venue_booking_provider.venue
        assert created_offer.description == "testDescription"
        assert created_offer.durationMinutes == 120
        assert created_offer.isDuo
        assert created_offer.subcategoryId == subcategories.SEANCE_CINE.id

        assert created_product.name == "movieTest"
        assert created_product.description == "testDescription"
        assert created_product.durationMinutes == 120
        assert created_product.extraData == {"visa": "123456"}
