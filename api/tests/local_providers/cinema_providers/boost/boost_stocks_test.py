import datetime

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.providers.factories import BoostCinemaDetailsFactory
from pcapi.core.providers.factories import CinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import BoostStocks

from . import fixtures


@pytest.mark.usefixtures("db_session")
class BoostStocksTest:
    def should_return_providable_info_on_next(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.TWO_FILMS_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/35278?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.DATA_1,
        )

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        providable_infos = next(boost_stocks)

        assert len(providable_infos) == 3

        product_providable_info = providable_infos[0]
        offer_providable_info = providable_infos[1]
        stock_providable_info = providable_infos[2]

        assert product_providable_info.type == Product
        assert product_providable_info.id_at_providers == "193"
        assert product_providable_info.new_id_at_provider == "193"

        assert offer_providable_info.type == Offer
        assert "193%" in offer_providable_info.id_at_providers
        assert "193%" in offer_providable_info.new_id_at_provider

        assert stock_providable_info.type == Stock
        assert "193%" in stock_providable_info.id_at_providers
        assert "#35278" in stock_providable_info.id_at_providers
        assert "193%" in stock_providable_info.new_id_at_provider
        assert "#35278" in stock_providable_info.new_id_at_provider

    def should_fill_offer_and_product_and_stock_informations_for_each_movie(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.TWO_FILMS_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/35278?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.DATA_1,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/35418?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.DATA_2,
        )

        boost_stocks = BoostStocks(venue_provider=venue_provider)

        boost_stocks.updateObjects()

        created_offers = Offer.query.order_by(Offer.id).all()
        created_products = Product.query.order_by(Product.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()
        assert len(created_stocks) == 2

        assert created_offers[0].name == "LE NOUVEAU JOUET"
        assert created_offers[0].product == created_products[0]
        assert created_offers[0].venue == venue_provider.venue
        assert not created_offers[0].description  # FIXME
        assert created_offers[0].durationMinutes == 1  # FIXME
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id

        assert created_products[0].name == "LE NOUVEAU JOUET"
        assert not created_products[0].description  # FIXME
        assert created_products[0].durationMinutes == 1  # FIXME
        assert created_products[0].extraData == {"visa": "155775"}

        assert created_stocks[0].quantity == 122
        assert created_stocks[0].price == 6.0
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2022, 10, 18, 22, 00)
        assert created_stocks[0].offer == created_offers[0]

        assert created_offers[1].name == "Avatar : La Voie De L'eau"
        assert created_offers[1].product == created_products[1]
        assert created_offers[1].venue == venue_provider.venue
        assert not created_offers[1].description  # FIXME
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id

        assert created_products[1].name == "Avatar : La Voie De L'eau"
        assert not created_products[1].description  # FIXME
        assert created_products[1].durationMinutes == 1  # FIXME
        assert created_products[1].extraData == {"visa": "123456"}

        assert created_stocks[1].quantity == 96
        assert created_stocks[1].price == 6.0
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2022, 10, 25, 22, 00)
        assert created_stocks[1].offer == created_offers[1]

    def should_not_create_stock_when_showtime_does_not_have_pass_culture_pricing(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/35418?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.DATA_SHOWTIME_WITHOUT_PC_PRICING,
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
        cinema_provider_pivot = CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/35418?filter_payment_method=external:credit:passculture",
            json=fixtures.ShowtimeDetailsEndpointResponse.DATA_2,
        )

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_stock = Stock.query.one()

        assert created_stock.quantity == 96

        created_stock.quantity = 100
        created_stock.dnBookedQuantity = 2

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_stocks = Stock.query.all()

        assert len(created_stocks) == 1
        assert created_stocks[0].quantity == 98
        assert created_stocks[0].dnBookedQuantity == 2
