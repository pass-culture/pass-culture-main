import datetime
from pathlib import Path

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
from pcapi.utils.human_ids import humanize

import tests

from . import fixtures


TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")
DATE_AFTER_30_DAYS_STR = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")


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
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{DATE_AFTER_30_DAYS_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{DATE_AFTER_30_DAYS_STR}?page=2&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_2_JSON_DATA,
        )
        requests_mock.get(
            # TODO(fseguin, 2023-02-06): add  ?filter_payment_method=external:credit:passculture when BB API is updated
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36848",
            json=fixtures.ShowtimeDetailsEndpointResponse.ONE_PCU_PRICING_SHOWTIME_36848_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36932",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36932_DATA_NO_PC_PRICING,
        )
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        providable_infos = next(boost_stocks)

        assert len(providable_infos) == 3
        product_providable_info = providable_infos[0]
        offer_providable_info = providable_infos[1]
        stock_providable_info = providable_infos[2]

        assert product_providable_info.type == Product
        assert product_providable_info.id_at_providers == f"207%{venue_provider.venue.id}%Boost"
        assert product_providable_info.new_id_at_provider == f"207%{venue_provider.venue.id}%Boost"

        assert offer_providable_info.type == Offer
        assert offer_providable_info.id_at_providers == f"207%{venue_provider.venue.id}%Boost"
        assert offer_providable_info.new_id_at_provider == f"207%{venue_provider.venue.id}%Boost"

        assert stock_providable_info.type == Stock
        assert stock_providable_info.id_at_providers == f"207%{venue_provider.venue.id}%Boost#36683"
        assert stock_providable_info.new_id_at_provider == f"207%{venue_provider.venue.id}%Boost#36683"

    def should_fill_offer_and_product_and_stock_informations_for_each_movie(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{DATE_AFTER_30_DAYS_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{DATE_AFTER_30_DAYS_STR}?page=2&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_2_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36848",
            json=fixtures.ShowtimeDetailsEndpointResponse.ONE_PCU_PRICING_SHOWTIME_36848_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36932",
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
        assert created_offers[0].extraData == {"visa": "158026"}

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
        assert created_offers[1].extraData == {"visa": "149489"}

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
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{DATE_AFTER_30_DAYS_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.NO_PC_PRICING_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36932",
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
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{DATE_AFTER_30_DAYS_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
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

    def should_create_product_with_correct_thumb(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{DATE_AFTER_30_DAYS_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            seagull_poster = thumb_file.read()
        requests_mock.get(
            "http://example.com/images/158026.jpg",
            content=seagull_poster,
        )

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_products = Product.query.order_by(Product.id).all()
        assert len(created_products) == 1
        assert (
            created_products[0].thumbUrl
            == f"http://localhost/storage/thumbs/products/{humanize(created_products[0].id)}"
        )
        assert created_products[0].thumbCount == 1

    def should_not_update_thumbnail_more_then_once_a_day(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{DATE_AFTER_30_DAYS_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        get_poster_adapter = requests_mock.get("http://example.com/images/158026.jpg", content=bytes())

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        assert get_poster_adapter.call_count == 1

        boost_stocks.updateObjects()

        assert get_poster_adapter.call_count == 1
