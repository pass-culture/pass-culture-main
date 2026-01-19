import datetime
import decimal
import logging
from pathlib import Path
from typing import Type
from unittest import mock
from unittest.mock import patch

import pytest
import time_machine

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.factories import EventProductFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.factories import ProductMediationFactory
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory
from pcapi.core.offers.models import PriceCategoryLabel
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.providers.etls.boost_etl import BoostExtractTransformLoadProcess
from pcapi.core.providers.factories import BoostCinemaDetailsFactory
from pcapi.core.providers.factories import BoostCinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import BoostStocks
from pcapi.models import db
from pcapi.utils.requests import exceptions as requests_exception

import tests

from . import fixtures


TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")
FUTURE_DATE_STR = (datetime.date.today() + datetime.timedelta(days=60)).strftime("%Y-%m-%d")


@pytest.mark.usefixtures("db_session")
class BoostStocksTest:
    def _create_products(self):
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

    def _get_product_by_allocine_id(self, allocine_id):
        return db.session.query(Product).filter(Product.extraData.op("->")("allocineId") == str(allocine_id)).one()

    def _create_cinema_and_pivot(self):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = VenueProviderFactory(provider=boost_provider, isDuoOffers=True, venue__pricing_point="self")
        cinema_provider_pivot = BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        BoostCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/")

        return venue_provider

    def execute_import(
        self,
        ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks],
        venue_provider,
    ) -> BoostExtractTransformLoadProcess | BoostStocks:
        boost_stocks = ProcessClass(venue_provider=venue_provider)
        if isinstance(boost_stocks, BoostStocks):
            boost_stocks.updateObjects()
        else:
            boost_stocks.execute()

        return boost_stocks

    # Not tested with `BoostETLProcess` because it is specific to the Iterator implementation
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

    @time_machine.travel(datetime.datetime(2023, 8, 11), tick=False)
    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def should_fill_offer_and_stock_information_for_each_movie_based_on_product(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        self._create_products()
        venue_provider = self._create_cinema_and_pivot()

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

        boost_stocks = self.execute_import(ProcessClass, venue_provider)
        if isinstance(boost_stocks, BoostStocks):
            assert boost_stocks.erroredObjects == 0
            assert boost_stocks.erroredThumbs == 0

        created_offers = db.session.query(Offer).order_by(Offer.id).all()
        created_stocks = db.session.query(Stock).order_by(Stock.id).all()
        created_price_categories = db.session.query(PriceCategory).order_by(PriceCategory.id).all()
        created_price_category_label = db.session.query(PriceCategoryLabel).one()
        assert len(created_offers) == 2
        assert len(created_stocks) == 3
        assert len(created_price_categories) == 3

        assert created_offers[0].name == "Produit allociné 3"
        assert created_offers[0].product == self._get_product_by_allocine_id(270935)
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddress == venue_provider.venue.offererAddress
        assert created_offers[0]._description is None
        assert created_offers[0].description == "Description du produit allociné 3"
        assert created_offers[0].durationMinutes == 333
        assert created_offers[0].isDuo
        assert created_offers[0].publicationDatetime == datetime.datetime(2023, 8, 11, tzinfo=datetime.UTC)
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].extraData == {"allocineId": 270935}
        assert created_offers[0]._extraData == {}

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
        assert created_offers[1]._description is None
        assert created_offers[1].description == "Description du produit allociné 4"
        assert created_offers[1].durationMinutes == 444
        assert created_offers[1].isDuo
        assert created_offers[1].publicationDatetime == datetime.datetime(2023, 8, 11, tzinfo=datetime.UTC)
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].extraData == {"allocineId": 269975}
        assert created_offers[1]._extraData == {}

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

        assert get_cinema_attr_adapter.call_count == 1

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def should_fill_offer_and_stocks_and_price_categories_based_on_product(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        self._create_products()
        venue_provider = self._create_cinema_and_pivot()

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.SAME_FILM_TWICE_JSON_DATA,
        )

        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        boost_stocks = self.execute_import(ProcessClass, venue_provider)
        if isinstance(boost_stocks, BoostStocks):
            assert boost_stocks.erroredObjects == 0
            assert boost_stocks.erroredThumbs == 0

        created_offer = db.session.query(Offer).order_by(Offer.id).one()
        created_stocks = db.session.query(Stock).order_by(Stock.id).all()
        created_price_categories = db.session.query(PriceCategory).order_by(PriceCategory.id).all()
        created_price_category_labels = db.session.query(PriceCategoryLabel).order_by(PriceCategoryLabel.label).all()
        assert len(created_price_categories) == 2
        assert len(created_price_category_labels) == 2

        assert created_offer.name == "Produit allociné 1"
        assert created_offer.product == self._get_product_by_allocine_id(263242)
        assert created_offer.venue == venue_provider.venue
        assert created_offer._description is None
        assert created_offer.description == "Description du produit allociné 1"
        assert created_offer.durationMinutes == 111
        assert created_offer.isDuo
        assert created_offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offer.extraData == {"allocineId": 263242}
        assert created_offer._extraData == {}

        assert created_stocks[0].quantity == 96
        assert created_stocks[0].price == decimal.Decimal("6.9")
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offer
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2022, 11, 28, 8)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2022, 11, 28, 8)

        assert created_stocks[1].quantity == 0
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

        assert get_cinema_attr_adapter.call_count == 1

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def should_reuse_price_category(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        venue_provider = self._create_cinema_and_pivot()

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())

        self.execute_import(ProcessClass, venue_provider)
        self.execute_import(ProcessClass, venue_provider)

        created_price_category = db.session.query(PriceCategory).one()
        assert created_price_category.price == decimal.Decimal("6.9")
        assert db.session.query(PriceCategoryLabel).count() == 1

        assert get_cinema_attr_adapter.call_count == 2

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def should_not_create_stock_when_showtime_does_not_have_pass_culture_pricing(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        venue_provider = self._create_cinema_and_pivot()

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.NO_PC_PRICING_JSON_DATA,
        )

        self.execute_import(ProcessClass, venue_provider)

        created_offers = db.session.query(Offer).order_by(Offer.id).all()
        created_stocks = db.session.query(Stock).order_by(Stock.id).all()

        assert len(created_offers) == 0
        assert len(created_stocks) == 0

        assert get_cinema_attr_adapter.call_count == 1

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def should_update_stock_with_the_correct_stock_quantity(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
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
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        self.execute_import(ProcessClass, venue_provider)
        created_stock = db.session.query(Stock).one()
        # we received numberSeatsForOnlineSale = 96
        assert created_stock.quantity == 96

        # make a duo booking
        bookings_factories.BookingFactory(stock=created_stock, quantity=2)

        assert created_stock.dnBookedQuantity == 2

        # synchronize with sold out show
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_WITH_SOLD_OUT_SHOWTIME_PAGE_1_JSON_DATA,
        )

        self.execute_import(ProcessClass, venue_provider)

        created_stocks = db.session.query(Stock).all()

        assert len(created_stocks) == 1
        assert created_stocks[0].quantity == 2
        assert created_stocks[0].dnBookedQuantity == 2

        assert get_cinema_attr_adapter.call_count == 2

    # Not tested with `BoostETLProcess` because it is logic that was implemented for a very specific Festival
    @patch("pcapi.local_providers.movie_festivals.constants.FESTIVAL_RATE", decimal.Decimal("4.0"))
    @patch("pcapi.local_providers.movie_festivals.constants.FESTIVAL_NAME", "My awesome festival")
    @patch("pcapi.local_providers.movie_festivals.api.should_apply_movie_festival_rate")
    def should_update_stock_with_movie_festival_rate(
        self,
        should_apply_movie_festival_rate_mock,
        requests_mock,
    ):
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
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        should_apply_movie_festival_rate_mock.return_value = True
        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        stock = db.session.query(Stock).one()

        assert stock.price == decimal.Decimal("4.0")
        assert stock.priceCategory.price == decimal.Decimal("4.0")
        assert stock.priceCategory.priceCategoryLabel.label == "My awesome festival"
        should_apply_movie_festival_rate_mock.assert_called_with(stock.offer.id, stock.beginningDatetime.date())

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def should_update_finance_event_when_stock_beginning_datetime_is_updated(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        venue_provider = self._create_cinema_and_pivot()

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

        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            self.execute_import(ProcessClass, venue_provider)
        mock_update_finance_event.assert_not_called()

        # synchronize again with same event date
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            self.execute_import(ProcessClass, venue_provider)
        mock_update_finance_event.assert_not_called()

        # synchronize again with new event date
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_WITH_NEW_DATE_JSON_DATA,
        )
        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            self.execute_import(ProcessClass, venue_provider)

        stock = db.session.query(offers_models.Stock).one()
        mock_update_finance_event.assert_called_with(stock)

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def test_should_create_product_mediation(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        venue_provider = self._create_cinema_and_pivot()
        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            seagull_poster = thumb_file.read()
        requests_mock.get(
            "http://example.com/images/158026.jpg",
            content=seagull_poster,
        )

        boost_stocks = self.execute_import(ProcessClass, venue_provider)
        if isinstance(boost_stocks, BoostStocks):
            assert boost_stocks.createdThumbs == 1
            assert boost_stocks.erroredThumbs == 0

        created_offer = db.session.query(Offer).one()

        assert created_offer.image.url == created_offer.product.productMediations[0].url
        assert get_cinema_attr_adapter.call_count == 1

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def test_should_not_create_product_mediation(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        venue_provider = self._create_cinema_and_pivot()
        requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )

        product = EventProductFactory(
            name=fixtures.FILM_207["titleCnc"],
            extraData=offers_models.OfferExtraData(
                allocineId=fixtures.FILM_207["idFilmAllocine"],
                visa=fixtures.FILM_207["numVisa"],
            ),
        )
        ProductMediationFactory(product=product, imageType=offers_models.ImageType.POSTER)

        get_image_adapter = requests_mock.get("http://example.com/images/158026.jpg")

        boost_stocks = self.execute_import(ProcessClass, venue_provider)

        if isinstance(boost_stocks, BoostStocks):
            assert boost_stocks.createdThumbs == 0

        assert not get_image_adapter.last_request

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def should_create_offer_even_if_incorrect_thumb(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        venue_provider = self._create_cinema_and_pivot()
        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        # Image that should raise a `pcapi.core.offers.exceptions.UnidentifiedImage`
        file_path = Path(tests.__path__[0]) / "files" / "mouette_fake_jpg.jpg"
        with open(file_path, "rb") as thumb_file:
            seagull_poster = thumb_file.read()
        requests_mock.get(
            "http://example.com/images/158026.jpg",
            content=seagull_poster,
        )

        boost_stocks = self.execute_import(ProcessClass, venue_provider)

        if isinstance(boost_stocks, BoostStocks):
            assert boost_stocks.erroredThumbs == 1

        created_offer = db.session.query(Offer).one()

        assert created_offer.activeMediation is None
        assert get_cinema_attr_adapter.call_count == 1

    # Not tested with `BoostETLProcess` because this logic was dropped with new implemnentation
    def should_not_update_thumbnail_more_then_once_a_day(self, requests_mock):
        venue_provider = self._create_cinema_and_pivot()
        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )
        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )

        get_poster_adapter = requests_mock.get("http://example.com/images/158026.jpg", content=bytes())

        boost_stocks = BoostStocks(venue_provider=venue_provider)
        boost_stocks.updateObjects()

        assert get_poster_adapter.call_count == 1

        boost_stocks.updateObjects()

        assert get_poster_adapter.call_count == 1

        assert get_cinema_attr_adapter.call_count == 1

    @pytest.mark.parametrize(
        "get_adapter_error_params",
        [
            # invalid responses
            {"status_code": 404},
            {"status_code": 502},
            # unexpected errors
            {"exc": requests_exception.ReadTimeout},
            {"exc": requests_exception.ConnectTimeout},
        ],
    )
    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def test_handle_error_on_movie_poster(
        self,
        ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks],
        get_adapter_error_params,
        requests_mock,
        caplog,
    ):
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
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?paymentMethod=external:credit:passculture&hideFullReservation=1&page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get("http://example.com/images/158026.jpg", **get_adapter_error_params)

        with caplog.at_level(logging.WARNING, logger="pcapi.core.external_bookings.models"):
            self.execute_import(ProcessClass, venue_provider)

        created_offer = db.session.query(Offer).one()
        assert created_offer.thumbUrl is None

        assert len(caplog.records) >= 1

        last_record = caplog.records.pop()
        assert last_record.message == "Could not fetch movie poster"
        assert last_record.extra == {"client": "BoostAPIClient", "url": "http://example.com/images/158026.jpg"}

    @pytest.mark.parametrize("ProcessClass", [BoostStocks, BoostExtractTransformLoadProcess])
    def should_link_offer_with_known_visa_to_product(
        self, ProcessClass: Type[BoostExtractTransformLoadProcess] | Type[BoostStocks], requests_mock
    ):
        venue_provider = self._create_cinema_and_pivot()

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
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())
        requests_mock.get("http://example.com/images/149489.jpg", content=bytes())

        product_1 = ProductFactory(name="Produit 1", extraData={"visa": "158026"})
        product_2 = ProductFactory(name="Produit 2", extraData={"visa": "149489"})

        self.execute_import(ProcessClass, venue_provider)

        created_offers = db.session.query(Offer).order_by(Offer.id).all()

        assert len(created_offers) == 2
        assert created_offers[0].product == product_1
        assert created_offers[1].product == product_2
