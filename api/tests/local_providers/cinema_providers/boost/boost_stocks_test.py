import datetime

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.providers.factories import BoostCinemaDetailsFactory
from pcapi.core.providers.factories import BoostCinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import BoostStocks

from . import fixtures


@pytest.mark.usefixtures("db_session")
class BoostStocksTest:
    def should_return_providable_info_on_next(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=2&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_2_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36683_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36848?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36848_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36932?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36932_DATA_NO_PC_PRICING,
        )
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        providable_infos = next(boost_stocks)

        assert len(providable_infos) == 3
        product_providable_info = providable_infos[0]
        offer_providable_info = providable_infos[1]
        stock_providable_info = providable_infos[2]

        assert product_providable_info.type == Product
        assert product_providable_info.id_at_providers == "207"
        assert product_providable_info.new_id_at_provider == "207"

        assert offer_providable_info.type == Offer
        assert "207%" in offer_providable_info.id_at_providers
        assert "207%" in offer_providable_info.new_id_at_provider

        assert stock_providable_info.type == Stock
        assert "207%" in stock_providable_info.id_at_providers
        assert "#36683" in stock_providable_info.id_at_providers
        assert "207%" in stock_providable_info.new_id_at_provider
        assert "#36683" in stock_providable_info.new_id_at_provider

    def should_fill_offer_and_product_and_stock_informations_for_each_movie(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=2&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_2_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36683_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36848?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36848_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36932?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36932_DATA_NO_PC_PRICING,
        )
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_offers = Offer.query.order_by(Offer.id).all()
        created_products = Product.query.order_by(Product.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()
        assert len(created_offers) == len(created_products) == 2
        assert len(created_stocks) == 2

        assert created_offers[0].name == "BLACK PANTHER : WAKANDA FOREVER"
        assert created_offers[0].product == created_products[0]
        assert created_offers[0].venue == venue_provider.venue
        assert not created_offers[0].description  # FIXME
        assert created_offers[0].durationMinutes == 162
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id

        assert created_products[0].name == "BLACK PANTHER : WAKANDA FOREVER"
        assert not created_products[0].description  # FIXME
        assert created_products[0].durationMinutes == 162
        assert created_products[0].extraData == {"visa": "158026"}

        assert created_stocks[0].quantity == 96
        assert created_stocks[0].price == 6.0
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime is None
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].beginningDatetime == datetime.datetime(2022, 11, 28, 8)

        assert created_offers[1].name == "CHARLOTTE"
        assert created_offers[1].product == created_products[1]
        assert created_offers[1].venue == venue_provider.venue
        assert not created_offers[1].description  # FIXME
        assert created_offers[1].durationMinutes == 92
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id

        assert created_products[1].name == "CHARLOTTE"
        assert not created_products[1].description  # FIXME
        assert created_products[1].durationMinutes == 92
        assert created_products[1].extraData == {"visa": "149489"}

        assert created_stocks[1].quantity == 177
        assert created_stocks[1].price == 6.0
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].bookingLimitDatetime is None
        assert created_stocks[1].offer == created_offers[1]
        assert created_stocks[1].beginningDatetime == datetime.datetime(2022, 11, 28, 8)

    def should_not_create_stock_when_showtime_does_not_have_pass_culture_pricing(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.NO_PC_PRICING_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36932?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36932_DATA_NO_PC_PRICING,
        )
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_offers = Offer.query.order_by(Offer.id).all()
        created_products = Product.query.order_by(Product.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()

        assert len(created_products) == 0
        assert len(created_offers) == 0
        assert len(created_stocks) == 0

    def should_update_stock_with_the_correct_stock_quantity(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36683_DATA,
        )
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()
        created_stock = Stock.query.one()
        # we received numberSeatsForOnlineSale = 96
        assert created_stock.quantity == 96

        # we manually edit the Stock
        created_stock.quantity = 100
        created_stock.dnBookedQuantity = 2

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_stocks = Stock.query.all()

        assert len(created_stocks) == 1
        # we still receive numberSeatsForOnlineSale = 96, so we edit our Stock.quantity to match reality
        assert created_stocks[0].quantity == 98
        assert created_stocks[0].dnBookedQuantity == 2
