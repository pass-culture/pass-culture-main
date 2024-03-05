import datetime
import decimal
from pathlib import Path
from unittest import mock

import pytest
import sqlalchemy as sa

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external_bookings.boost import constants as boost_constants
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory
from pcapi.core.offers.models import PriceCategoryLabel
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.providers.factories import BoostCinemaDetailsFactory
from pcapi.core.providers.factories import BoostCinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.testing import override_features
from pcapi.local_providers import BoostStocks
from pcapi.repository import transaction
from pcapi.utils.human_ids import humanize

import tests

from . import fixtures


TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")
FUTURE_DATE_STR = (datetime.date.today() + datetime.timedelta(days=boost_constants.BOOST_SHOWS_INTERVAL_DAYS)).strftime(
    "%Y-%m-%d"
)


@pytest.mark.usefixtures("db_session")
class BoostStocksTest:
    def setup_method(self):
        ProductFactory(
            name="Produit allociné 1",
            description="Description du produit allociné 1",
            durationMinutes=111,
            extraData={"allocineId": 263242},
        )
        ProductFactory(
            name="Produit allociné 2",
            description="Description du produit allociné 2",
            durationMinutes=222,
            extraData={"allocineId": 277733},
        )
        ProductFactory(
            name="Produit allociné 3",
            description="Description du produit allociné 3",
            durationMinutes=333,
            extraData={"allocineId": 270935},
        )
        ProductFactory(
            name="Produit allociné 4",
            description="Description du produit allociné 4",
            durationMinutes=444,
            extraData={"allocineId": 269975},
        )

    def teardown_method(self):
        with transaction():
            Product.query.delete()

    def _get_product_by_allocine_id(self, allocine_id):
        return Product.query.filter(Product.extraData["allocineId"].cast(sa.Integer) == allocine_id).one()

    def should_return_providable_info_on_next(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=2&per_page=30",
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

        assert len(providable_infos) == 2
        offer_providable_info = providable_infos[0]
        stock_providable_info = providable_infos[1]

        assert offer_providable_info.type == Offer
        assert offer_providable_info.id_at_providers == f"207%{venue_provider.venue.id}%Boost"
        assert offer_providable_info.new_id_at_provider == f"207%{venue_provider.venue.id}%Boost"

        assert stock_providable_info.type == Stock
        assert stock_providable_info.id_at_providers == f"207%{venue_provider.venue.id}%Boost#36683"
        assert stock_providable_info.new_id_at_provider == f"207%{venue_provider.venue.id}%Boost#36683"

        assert get_cinema_attr_adapter.call_count == 1

    @override_features(WIP_ENABLE_BOOST_SHOWTIMES_FILTER=True)
    def should_return_providable_info_on_next_with_enabled_filter_ff(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?paymentMethod=external:credit:passculture&hideFullReservation=1&page=1&per_page=30",
            json=fixtures.ShowtimesWithPaymentMethodFilterEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?paymentMethod=external:credit:passculture&hideFullReservation=1&page=2&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_2_JSON_DATA,
        )

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        providable_infos = next(boost_stocks)

        assert len(providable_infos) == 2
        offer_providable_info = providable_infos[0]
        stock_providable_info = providable_infos[1]

        assert offer_providable_info.type == Offer
        assert offer_providable_info.id_at_providers == f"161%{venue_provider.venue.id}%Boost"
        assert offer_providable_info.new_id_at_provider == f"161%{venue_provider.venue.id}%Boost"

        assert stock_providable_info.type == Stock
        assert stock_providable_info.id_at_providers == f"161%{venue_provider.venue.id}%Boost#15971"
        assert stock_providable_info.new_id_at_provider == f"161%{venue_provider.venue.id}%Boost#15971"

        assert get_cinema_attr_adapter.call_count == 1

    def should_not_create_offers_and_stocks_if_products_dont_exist(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=2&per_page=30",
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
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        requests_mock.get("http://example.com/images/149489.jpg", content=bytes())

        Product.query.delete()

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        assert Offer.query.count() == 0
        assert Stock.query.count() == 0
        assert PriceCategory.query.count() == 0

    def should_fill_offer_and_and_stock_informations_for_each_movie(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=2&per_page=30",
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
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        requests_mock.get("http://example.com/images/149489.jpg", content=bytes())

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_offers = Offer.query.order_by(Offer.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_label = PriceCategoryLabel.query.one()
        assert len(created_offers) == 2
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2

        assert created_offers[0].name == "Produit allociné 1"
        assert created_offers[0].product == self._get_product_by_allocine_id(263242)
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].description == "Description du produit allociné 1"
        assert created_offers[0].durationMinutes == 111
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].extraData == {"visa": "158026", "allocineId": 263242}

        assert created_stocks[0].quantity == 96
        assert created_stocks[0].price == decimal.Decimal("6.9")
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2022, 11, 28, 8)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2022, 11, 28, 8)
        assert created_stocks[0].features == ["VF", "ICE"]

        assert created_offers[1].name == "Produit allociné 2"
        assert created_offers[1].product == self._get_product_by_allocine_id(277733)
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Description du produit allociné 2"
        assert created_offers[1].durationMinutes == 222
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].extraData == {"visa": "149489", "allocineId": 277733}

        assert created_stocks[1].quantity == 177
        assert created_stocks[1].price == decimal.Decimal("6.9")
        assert created_stocks[1].priceCategory == created_price_categories[1]
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offers[1]
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2022, 11, 28, 8)
        assert created_stocks[1].beginningDatetime == datetime.datetime(2022, 11, 28, 8)
        assert created_stocks[1].features == ["VO", "3D"]

        assert all((category.price == decimal.Decimal("6.9") for category in created_price_categories))
        assert all(
            (category.priceCategoryLabel == created_price_category_label for category in created_price_categories)
        )
        assert created_price_category_label.label == "PASS CULTURE"

        assert boost_stocks.erroredObjects == 0
        assert boost_stocks.erroredThumbs == 0

        assert get_cinema_attr_adapter.call_count == 1

    @override_features(WIP_ENABLE_BOOST_SHOWTIMES_FILTER=True)
    def should_fill_offer_and_stock_informations_for_each_movie_with_enabled_filter_ff(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?paymentMethod=external:credit:passculture&hideFullReservation=1&page=1&per_page=30",
            json=fixtures.ShowtimesWithPaymentMethodFilterEndpointResponse.PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?paymentMethod=external:credit:passculture&hideFullReservation=1&page=2&per_page=30",
            json=fixtures.ShowtimesWithPaymentMethodFilterEndpointResponse.PAGE_2_JSON_DATA,
        )
        requests_mock.get("http://example.com/images/159673.jpg", content=bytes())
        requests_mock.get("http://example.com/images/159570.jpg", content=bytes())

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_offers = Offer.query.order_by(Offer.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_label = PriceCategoryLabel.query.one()
        assert len(created_offers) == 2
        assert len(created_stocks) == 3
        assert len(created_price_categories) == 3

        assert created_offers[0].name == "Produit allociné 3"
        assert created_offers[0].product == self._get_product_by_allocine_id(270935)
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].description == "Description du produit allociné 3"
        assert created_offers[0].durationMinutes == 333
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].extraData == {"visa": "159673", "allocineId": 270935}

        assert created_stocks[0].quantity == 147
        assert created_stocks[0].price == decimal.Decimal("12.00")
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 9, 26, 8, 40)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 9, 26, 8, 40)
        assert created_stocks[0].features == ["VF", "ICE"]

        assert created_offers[1].name == "Produit allociné 4"
        assert created_offers[1].product == self._get_product_by_allocine_id(269975)
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Description du produit allociné 4"
        assert created_offers[1].durationMinutes == 444
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].extraData == {"visa": "159570", "allocineId": 269975}

        assert created_stocks[1].quantity == 452
        assert created_stocks[1].price == decimal.Decimal("6.00")
        assert created_stocks[1].priceCategory == created_price_categories[1]
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offers[1]
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2023, 9, 26, 9, 10)
        assert created_stocks[1].beginningDatetime == datetime.datetime(2023, 9, 26, 9, 10)
        assert created_stocks[1].features == ["VO"]

        assert created_stocks[2].offer == created_offers[1]

        assert created_stocks[2].quantity == 152
        assert created_stocks[2].price == decimal.Decimal("12.00")
        assert created_stocks[2].priceCategory == created_price_categories[2]
        assert created_stocks[2].dateCreated is not None
        assert created_stocks[2].offer == created_offers[1]
        assert created_stocks[2].bookingLimitDatetime == datetime.datetime(2023, 9, 26, 12, 20)
        assert created_stocks[2].beginningDatetime == datetime.datetime(2023, 9, 26, 12, 20)
        assert created_stocks[2].features == ["VF", "ICE"]

        assert created_price_categories[0].price == decimal.Decimal("12.00")
        assert created_price_categories[1].price == decimal.Decimal("6.00")
        assert created_price_categories[2].price == decimal.Decimal("12.00")

        assert all(
            (category.priceCategoryLabel == created_price_category_label for category in created_price_categories)
        )
        assert created_price_category_label.label == "PASS CULTURE"

        assert boost_stocks.erroredObjects == 0
        assert boost_stocks.erroredThumbs == 0

        assert get_cinema_attr_adapter.call_count == 1

    def should_fill_offer_and_stocks_and_price_categories(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.SAME_FILM_TWICE_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36684",
            json=fixtures.ShowtimeDetailsEndpointResponse.PC2_AND_FULL_PRICINGS_SHOWTIME_36684_DATA,
        )
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_offer = Offer.query.order_by(Offer.id).one()
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_labels = PriceCategoryLabel.query.order_by(PriceCategoryLabel.label).all()
        assert len(created_price_categories) == 2
        assert len(created_price_category_labels) == 2

        assert created_offer.name == "Produit allociné 1"
        assert created_offer.product == self._get_product_by_allocine_id(263242)
        assert created_offer.venue == venue_provider.venue
        assert created_offer.description == "Description du produit allociné 1"
        assert created_offer.durationMinutes == 111
        assert created_offer.isDuo
        assert created_offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offer.extraData == {"visa": "158026", "allocineId": 263242}

        assert created_stocks[0].quantity == 96
        assert created_stocks[0].price == decimal.Decimal("6.9")
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offer
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2022, 11, 28, 8)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2022, 11, 28, 8)

        assert created_stocks[1].quantity == 130
        assert created_stocks[1].price == 18.0
        assert created_stocks[1].priceCategory == created_price_categories[1]
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offer
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2022, 11, 29, 8)
        assert created_stocks[1].beginningDatetime == datetime.datetime(2022, 11, 29, 8)

        assert created_price_categories[0].price == decimal.Decimal("6.9")
        assert created_price_categories[0].label == "PASS CULTURE"
        assert created_price_categories[0].priceCategoryLabel == created_price_category_labels[0]

        assert created_price_categories[1].price == 18.0
        assert created_price_categories[1].label == "PASS CULTURE 1"
        assert created_price_categories[1].priceCategoryLabel == created_price_category_labels[1]

        assert boost_stocks.erroredObjects == 0
        assert boost_stocks.erroredThumbs == 0

        assert get_cinema_attr_adapter.call_count == 1

    def should_reuse_price_category(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())

        BoostStocks(venue_provider=venue_provider).updateObjects()
        BoostStocks(venue_provider=venue_provider).updateObjects()

        created_price_category = PriceCategory.query.one()
        assert created_price_category.price == decimal.Decimal("6.9")
        assert PriceCategoryLabel.query.count() == 1

        assert get_cinema_attr_adapter.call_count == 2

    def should_not_create_stock_when_showtime_does_not_have_pass_culture_pricing(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.NO_PC_PRICING_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36932",
            json=fixtures.ShowtimeDetailsEndpointResponse.SHOWTIME_36932_DATA_NO_PC_PRICING,
        )
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_offers = Offer.query.order_by(Offer.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()

        assert len(created_offers) == 0
        assert len(created_stocks) == 0

        assert get_cinema_attr_adapter.call_count == 1

    def should_update_stock_with_the_correct_stock_quantity(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()
        created_stock = Stock.query.one()
        # we received numberSeatsForOnlineSale = 96
        assert created_stock.quantity == 96

        # make a duo booking
        bookings_factories.BookingFactory(stock=created_stock, quantity=2)

        assert created_stock.dnBookedQuantity == 2

        # synchronize with sold out show
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.SOLD_OUT_SHOWTIME_36683_DATA,
        )

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_stocks = Stock.query.all()

        assert len(created_stocks) == 1
        assert created_stocks[0].quantity == 2
        assert created_stocks[0].dnBookedQuantity == 2

        assert get_cinema_attr_adapter.call_count == 2

    def should_update_finance_event_when_stock_beginning_datetime_is_updated(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            boost_stocks.updateObjects()
        mock_update_finance_event.assert_not_called()

        # synchronize again with same event date
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            boost_stocks.updateObjects()
        mock_update_finance_event.assert_not_called()

        # synchronize again with new event date
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA_WITH_NEW_DATE,
        )
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            boost_stocks.updateObjects()
        mock_update_finance_event.assert_called_once()

    def should_create_offer_with_correct_thumb(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")
        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
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

        created_offer = Offer.query.one()
        assert (
            created_offer.thumbUrl
            == f"http://localhost/storage/thumbs/mediations/{humanize(created_offer.activeMediation.id)}"
        )
        assert created_offer.activeMediation.thumbCount == 1

        assert boost_stocks.erroredThumbs == 0

        assert get_cinema_attr_adapter.call_count == 1

    def should_not_update_thumbnail_more_then_once_a_day(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")
        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
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

        assert get_cinema_attr_adapter.call_count == 1

    def test_handle_error_on_movie_poster(self, requests_mock):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot,
            cinemaUrl="https://cinema-0.example.com/",
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs",
            json=fixtures.CinemasAttributsEndPointResponse.DATA,
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/36683",
            json=fixtures.ShowtimeDetailsEndpointResponse.THREE_PRICINGS_SHOWTIME_36683_DATA,
        )
        requests_mock.get("http://example.com/images/158026.jpg", status_code=404)

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        created_offer = Offer.query.one()
        assert created_offer.thumbUrl is None
