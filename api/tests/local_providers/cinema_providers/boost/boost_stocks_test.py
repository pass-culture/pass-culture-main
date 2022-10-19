import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.serialization.boost_serializers import Film2
from pcapi.connectors.serialization.boost_serializers import ShowTime3
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.providers.factories import BoostCinemaDetailsFactory
from pcapi.core.providers.factories import CinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import BoostStocks


@pytest.mark.usefixtures("db_session")
class BoostStocksTest:
    @patch("pcapi.local_providers.cinema_providers.boost.boost_stocks.BoostStocks._get_showtimes")
    def should_get_showtimes(self, mocked_get_showtimes):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        film = Film2(
            id=1,
            titleCnc="Black Adam",
            numVisa="253389",
            posterUrl="http://example.com/images/253389.jpg",
            thumbUrl="http://example.com/img/thumb/film/253389.jpg",
            idFilmAllocine=253389,
        )
        showtimes_mock = [
            ShowTime3(
                id=1,
                showDate=datetime.datetime(2022, 10, 24, 10, 00),
                showEndDate=datetime.datetime(2022, 10, 24, 12, 00),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=20,
                film=film,
                format={},
                version={},
                screen={},
            ),
            ShowTime3(
                id=2,
                showDate=datetime.datetime(2022, 10, 24, 16, 00),
                showEndDate=datetime.datetime(2022, 10, 24, 18, 00),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=40,
                film=film,
                format={},
                version={},
                screen={},
            ),
        ]
        mocked_get_showtimes.return_value = showtimes_mock

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_showtimes = list(boost_stocks.showtimes)

        mocked_get_showtimes.assert_called_once()
        assert len(boost_showtimes) == 2

    @patch("pcapi.local_providers.cinema_providers.boost.boost_stocks.BoostStocks._get_showtimes")
    def should_return_providable_info_on_next(self, mocked_get_showtimes):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        film = Film2(
            id=1234,
            titleCnc="Black Adam",
            numVisa="253389",
            posterUrl="http://example.com/images/253389.jpg",
            thumbUrl="http://example.com/img/thumb/film/253389.jpg",
            idFilmAllocine=253389,
        )
        showtimes_mock = [
            ShowTime3(
                id=1,
                showDate=datetime.datetime(2022, 10, 24, 10, 00),
                showEndDate=datetime.datetime(2022, 10, 24, 12, 00),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=20,
                film=film,
                format={},
                version={},
                screen={},
            ),
        ]
        mocked_get_showtimes.return_value = showtimes_mock

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        providable_infos = next(boost_stocks)

        assert len(providable_infos) == 3

        product_providable_info = providable_infos[0]
        offer_providable_info = providable_infos[1]
        stock_providable_info = providable_infos[2]

        assert product_providable_info.type == Product
        assert product_providable_info.id_at_providers == "1234"
        assert product_providable_info.new_id_at_provider == "1234"

        assert offer_providable_info.type == Offer
        assert "1234%" in offer_providable_info.id_at_providers
        assert "1234%" in offer_providable_info.new_id_at_provider

        assert stock_providable_info.type == Stock
        assert "1234%" in stock_providable_info.id_at_providers
        assert "#1" in stock_providable_info.id_at_providers
        assert "1234%" in stock_providable_info.new_id_at_provider
        assert "#1" in stock_providable_info.new_id_at_provider

    @patch("pcapi.local_providers.cinema_providers.boost.boost_stocks.BoostStocks._get_showtimes")
    def should_fill_offer_and_product_and_stock_informations_for_each_movie(self, mocked_showtimes):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        film_1 = Film2(
            id=1234,
            titleCnc="Black Adam",
            numVisa="253389",
            posterUrl="http://example.com/images/253389.jpg",
            thumbUrl="http://example.com/img/thumb/film/253389.jpg",
            idFilmAllocine=253389,
        )
        film_2 = Film2(
            id=5678,
            titleCnc="Mascarade",
            numVisa="153521",
            posterUrl="http://example.com/images/153521.jpg",
            thumbUrl="http://example.com/img/thumb/film/153521.jpg",
            idFilmAllocine=289268,
        )
        showtimes_mock = [
            ShowTime3(
                id=1,
                showDate=datetime.datetime(2022, 10, 24, 10, 00),
                showEndDate=datetime.datetime(2022, 10, 24, 12, 00),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=20,
                film=film_1,
                format={},
                version={},
                screen={},
            ),
            ShowTime3(
                id=2,
                showDate=datetime.datetime(2022, 10, 24, 16, 00),
                showEndDate=datetime.datetime(2022, 10, 24, 18, 00),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=40,
                film=film_2,
                format={},
                version={},
                screen={},
            ),
        ]
        mocked_showtimes.return_value = showtimes_mock

        boost_stocks = BoostStocks(venue_provider=venue_provider)

        boost_stocks.updateObjects()

        created_offers = Offer.query.order_by(Offer.id).all()
        created_products = Product.query.order_by(Product.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()
        assert len(created_stocks) == 2

        assert created_offers[0].name == "Black Adam"
        assert created_offers[0].product == created_products[0]
        assert created_offers[0].venue == venue_provider.venue
        assert not created_offers[0].description  # FIXME
        assert created_offers[0].durationMinutes == 1  # FIXME
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id

        assert created_products[0].name == "Black Adam"
        assert not created_products[0].description  # FIXME
        assert created_products[0].durationMinutes == 1  # FIXME
        assert created_products[0].extraData == {"visa": "253389"}

        assert created_stocks[0].quantity == 20
        assert created_stocks[0].price == 5.0
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2022, 10, 23, 22, 00)
        assert created_stocks[0].offer == created_offers[0]

        assert created_offers[1].name == "Mascarade"
        assert created_offers[1].product == created_products[1]
        assert created_offers[1].venue == venue_provider.venue
        assert not created_offers[1].description  # FIXME
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id

        assert created_products[1].name == "Mascarade"
        assert not created_products[1].description  # FIXME
        assert created_products[1].durationMinutes == 1  # FIXME
        assert created_products[1].extraData == {"visa": "153521"}

        assert created_stocks[1].quantity == 40
        assert created_stocks[1].price == 5.0
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2022, 10, 23, 22, 00)
        assert created_stocks[1].offer == created_offers[1]
