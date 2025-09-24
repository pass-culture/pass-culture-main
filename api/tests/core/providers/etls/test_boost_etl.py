import datetime
import decimal
import logging
import pathlib
from decimal import Decimal
from unittest import mock

import pytest
import time_machine

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.core.providers.clients import boost_client
from pcapi.core.providers.clients import boost_serializers
from pcapi.core.providers.etls.boost_etl import BoostExtractTransformLoadProcess
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.search import models as search_models
from pcapi.models import db
from pcapi.utils import requests

import tests

from . import fixtures


pytestmark = pytest.mark.usefixtures("db_session")

TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")
FUTURE_DATE_STR = (datetime.date.today() + datetime.timedelta(days=boost_client.BOOST_SHOWS_INTERVAL_DAYS)).strftime(
    "%Y-%m-%d"
)


class BoostExtractTransformLoadProcessTest:
    def setup_cinema_objects(self):
        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            provider=boost_provider, isDuoOffers=True, venue__pricing_point="self"
        )
        cinema_provider_pivot = providers_factories.BoostCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.BoostCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/"
        )

        return venue_provider

    def setup_requests_mock(self, requests_mock) -> None:
        requests_mock.get(
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

    def test_execute_should_raise_inactive_provider(self):
        venue_provider = self.setup_cinema_objects()
        venue_provider.provider.isActive = False
        etl_process = BoostExtractTransformLoadProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveProvider):
            etl_process.execute()

    def test_execute_should_raise_inactive_venue_provider_provider(self):
        venue_provider = self.setup_cinema_objects()
        venue_provider.isActive = False
        etl_process = BoostExtractTransformLoadProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveVenueProvider):
            etl_process.execute()

    def test_should_log_and_raise_error_if_extract_fails(self, caplog, requests_mock):
        venue_provider = self.setup_cinema_objects()
        etl_process = BoostExtractTransformLoadProcess(venue_provider)
        requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs",
            exc=requests.exceptions.ConnectTimeout("je suis sous l'eau"),
        )

        with caplog.at_level(logging.WARNING):
            with pytest.raises(requests.exceptions.ConnectTimeout):
                etl_process.execute()

        assert len(caplog.records) >= 1
        last_record = caplog.records[-1]
        assert last_record.message == "[BoostExtractTransformLoadProcess] Step 1 - Extract failed"
        assert last_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {"exc": "ConnectTimeout", "msg": "je suis sous l'eau"},
        }

    def test_extract_should_return_raw_results(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)

        etl_process = BoostExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        assert extract_result == {
            "cinema_attributes": [
                boost_serializers.CinemaAttribut(id=34, title="3D Passive"),
                boost_serializers.CinemaAttribut(id=35, title="4K"),
                boost_serializers.CinemaAttribut(id=45, title="7.1"),
                boost_serializers.CinemaAttribut(id=1, title="Accès PMR"),
                boost_serializers.CinemaAttribut(id=16, title="Coup de coeur"),
                boost_serializers.CinemaAttribut(id=44, title="Dolby Atmos"),
                boost_serializers.CinemaAttribut(id=17, title="Entracte"),
                boost_serializers.CinemaAttribut(id=5, title="Fidelio (Dolby Doremi)"),
                boost_serializers.CinemaAttribut(id=38, title="HFR"),
                boost_serializers.CinemaAttribut(id=24, title="ICE Immersive"),
                boost_serializers.CinemaAttribut(id=40, title="Laser"),
                boost_serializers.CinemaAttribut(id=19, title="MX4D"),
                boost_serializers.CinemaAttribut(id=51, title="Numérique"),
                boost_serializers.CinemaAttribut(id=28, title="Sièges Inclinables"),
                boost_serializers.CinemaAttribut(id=29, title="Sièges Inclinables électriques"),
            ],
            "showtimes": [
                boost_serializers.ShowTime4(
                    id=15971,
                    numberSeatsRemaining=147,
                    showDate=datetime.datetime(2023, 9, 26, 8, 40),
                    showEndDate=datetime.datetime(2023, 9, 26, 11, 38),
                    film=boost_serializers.Film2(
                        id=161,
                        titleCnc="MISSION IMPOSSIBLE DEAD RECKONING PARTIE 1",
                        numVisa=159673,
                        posterUrl="http://example.com/images/159673.jpg",
                        thumbUrl="http://example.com/img/thumb/film/159673.jpg",
                        duration=163,
                        idFilmAllocine=270935,
                    ),
                    format={"id": 1, "title": "2D"},
                    version={"id": 3, "title": "Film Etranger en Langue Française", "code": "VF"},
                    screen={
                        "id": 6,
                        "auditoriumNumber": 6,
                        "name": "SALLE 6 - ICE",
                        "capacity": 152,
                        "HFR": True,
                        "is4K": True,
                        "ice": True,
                        "lightVibes": True,
                        "eclairColor": False,
                        "hearingImpaired": False,
                        "audioDescription": False,
                        "seatingAllowed": True,
                        "screenPosition": False,
                    },
                    showtimePricing=[
                        boost_serializers.ShowtimePricing(
                            id=537105, pricingCode="PCU", amountTaxesIncluded=Decimal("12.0"), title="PASS CULTURE"
                        )
                    ],
                    attributs=[35, 44, 24, 1, 29, 40],
                ),
                boost_serializers.ShowTime4(
                    id=16277,
                    numberSeatsRemaining=452,
                    showDate=datetime.datetime(2023, 9, 26, 9, 10),
                    showEndDate=datetime.datetime(2023, 9, 26, 11, 45),
                    film=boost_serializers.Film2(
                        id=145,
                        titleCnc="SPIDER-MAN ACROSS THE SPIDER-VERSE",
                        numVisa=159570,
                        posterUrl="http://example.com/images/159570.jpg",
                        thumbUrl="http://example.com/img/thumb/film/159570.jpg",
                        duration=140,
                        idFilmAllocine=269975,
                    ),
                    format={"id": 1, "title": "2D"},
                    version={"id": 2, "title": "Film Etranger en Langue Etrangère", "code": "VO"},
                    screen={
                        "id": 2,
                        "auditoriumNumber": 2,
                        "name": "SALLE 2",
                        "capacity": 452,
                        "HFR": True,
                        "is4K": True,
                        "ice": False,
                        "lightVibes": False,
                        "eclairColor": False,
                        "hearingImpaired": False,
                        "audioDescription": False,
                        "seatingAllowed": True,
                        "screenPosition": False,
                    },
                    showtimePricing=[
                        boost_serializers.ShowtimePricing(
                            id=537354, pricingCode="PCU", amountTaxesIncluded=Decimal("6.0"), title="PASS CULTURE"
                        )
                    ],
                    attributs=[51, 45, 1, 40],
                ),
                boost_serializers.ShowTime4(
                    id=15978,
                    numberSeatsRemaining=152,
                    showDate=datetime.datetime(2023, 9, 26, 12, 20),
                    showEndDate=datetime.datetime(2023, 9, 26, 14, 55),
                    film=boost_serializers.Film2(
                        id=145,
                        titleCnc="SPIDER-MAN ACROSS THE SPIDER-VERSE",
                        numVisa=159570,
                        posterUrl="http://example.com/images/159570.jpg",
                        thumbUrl="http://example.com/img/thumb/film/159570.jpg",
                        duration=140,
                        idFilmAllocine=269975,
                    ),
                    format={"id": 1, "title": "2D"},
                    version={"id": 3, "title": "Film Etranger en Langue Française", "code": "VF"},
                    screen={
                        "id": 6,
                        "auditoriumNumber": 6,
                        "name": "SALLE 6 - ICE",
                        "capacity": 152,
                        "HFR": True,
                        "is4K": True,
                        "ice": True,
                        "lightVibes": True,
                        "eclairColor": False,
                        "hearingImpaired": False,
                        "audioDescription": False,
                        "seatingAllowed": True,
                        "screenPosition": False,
                    },
                    showtimePricing=[
                        boost_serializers.ShowtimePricing(
                            id=537132, pricingCode="PCU", amountTaxesIncluded=Decimal("12.0"), title="PASS CULTURE"
                        )
                    ],
                    attributs=[24, 1, 29, 40],
                ),
            ],
        }

    def test_transform_should_return_loadable_result(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        etl_process = BoostExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        transform_result = etl_process._transform(extract_result=extract_result)
        assert transform_result == [
            {
                "movie_uuid": f"161%{venue_id}%Boost",
                "movie_data": offers_models.Movie(
                    allocine_id="270935",
                    description=None,
                    duration=163,
                    poster_url="http://example.com/images/159673.jpg",
                    visa="159673",
                    title="MISSION IMPOSSIBLE DEAD RECKONING PARTIE 1",
                    extra_data=None,
                ),
                "stocks_data": [
                    {
                        "stock_uuid": f"161%{venue_id}%Boost#15971",
                        "show_datetime": datetime.datetime(2023, 9, 26, 8, 40),
                        "remaining_quantity": 147,
                        "features": ["VF", "ICE"],
                        "price": decimal.Decimal("12.0"),
                        "price_label": "PASS CULTURE",
                    }
                ],
            },
            {
                "movie_uuid": f"145%{venue_id}%Boost",
                "movie_data": offers_models.Movie(
                    allocine_id="269975",
                    description=None,
                    duration=140,
                    poster_url="http://example.com/images/159570.jpg",
                    visa="159570",
                    title="SPIDER-MAN ACROSS THE SPIDER-VERSE",
                    extra_data=None,
                ),
                "stocks_data": [
                    {
                        "stock_uuid": f"145%{venue_id}%Boost#16277",
                        "show_datetime": datetime.datetime(2023, 9, 26, 9, 10),
                        "remaining_quantity": 452,
                        "features": ["VO"],
                        "price": decimal.Decimal("6.0"),
                        "price_label": "PASS CULTURE",
                    },
                    {
                        "stock_uuid": f"145%{venue_id}%Boost#15978",
                        "show_datetime": datetime.datetime(2023, 9, 26, 12, 20),
                        "remaining_quantity": 152,
                        "features": ["VF", "ICE"],
                        "price": decimal.Decimal("12.0"),
                        "price_label": "PASS CULTURE",
                    },
                ],
            },
        ]

    def test_transform_should_drop_showtime_without_pc_pricing(self):
        venue_provider = self.setup_cinema_objects()
        etl_process = BoostExtractTransformLoadProcess(venue_provider)

        extract_result = {
            "cinema_attributes": [],
            "showtimes": [
                boost_serializers.ShowTime4(
                    id=15971,
                    numberSeatsRemaining=147,
                    showDate=datetime.datetime(2023, 9, 26, 8, 40),
                    showEndDate=datetime.datetime(2023, 9, 26, 11, 38),
                    film=boost_serializers.Film2(
                        id=161,
                        titleCnc="MISSION IMPOSSIBLE DEAD RECKONING PARTIE 1",
                        numVisa=159673,
                        posterUrl="http://example.com/images/159673.jpg",
                        thumbUrl="http://example.com/img/thumb/film/159673.jpg",
                        duration=163,
                        idFilmAllocine=270935,
                    ),
                    format={"id": 1, "title": "2D"},
                    version={"id": 3, "title": "Film Etranger en Langue Française", "code": "VF"},
                    screen={
                        "id": 6,
                        "auditoriumNumber": 6,
                        "name": "SALLE 6 - ICE",
                        "capacity": 152,
                        "HFR": True,
                        "is4K": True,
                        "ice": True,
                        "lightVibes": True,
                        "eclairColor": False,
                        "hearingImpaired": False,
                        "audioDescription": False,
                        "seatingAllowed": True,
                        "screenPosition": False,
                    },
                    showtimePricing=[
                        boost_serializers.ShowtimePricing(
                            id=537105,
                            pricingCode="FULL_PRICE",
                            amountTaxesIncluded=Decimal("14.0"),
                            title="Plein tarif",
                        )
                    ],
                    attributs=[35, 44, 24, 1, 29, 40],
                ),
            ],
        }
        transform_result = etl_process._transform(extract_result)
        assert transform_result == []

    @time_machine.travel(datetime.datetime(2023, 8, 12, 12, 41, 30), tick=False)
    def test_load_should_create_product_offer_and_stocks(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        etl_process = BoostExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        transform_result = etl_process._transform(extract_result=extract_result)
        offers_id, products_with_poster = etl_process._load(transform_result)

        offer_1 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"161%{venue_id}%Boost").one_or_none()
        offer_2 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"145%{venue_id}%Boost").one_or_none()

        assert offer_1
        assert offer_1.idAtProvider == f"161%{venue_id}%Boost"
        assert offer_1.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_1.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_1.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_1.publicationDatetime == datetime.datetime(2023, 8, 12, 12, 41, 30)

        assert offer_1.product
        assert offer_1.product.name == "MISSION IMPOSSIBLE DEAD RECKONING PARTIE 1"
        assert offer_1.product.durationMinutes == 163
        assert offer_1.product.extraData["allocineId"] == 270935
        assert offer_1.product.extraData["visa"] == "159673"

        assert offer_2
        assert offer_2.idAtProvider == f"145%{venue_id}%Boost"
        assert offer_2.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_2.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_2.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_2.publicationDatetime == datetime.datetime(2023, 8, 12, 12, 41, 30)

        assert offer_2.product
        assert offer_2.product.name == "SPIDER-MAN ACROSS THE SPIDER-VERSE"
        assert offer_2.product.durationMinutes == 140
        assert offer_2.product.extraData["allocineId"] == 269975
        assert offer_2.product.extraData["visa"] == "159570"

        assert offers_id == set([offer_1.id, offer_2.id])

        offer_1_stocks = offer_1.activeStocks
        assert len(offer_1_stocks) == 1
        offer_1_stock_1 = offer_1_stocks[0]
        assert offer_1_stock_1.idAtProviders == f"161%{venue_id}%Boost#15971"
        assert offer_1_stock_1.beginningDatetime == datetime.datetime(2023, 9, 26, 8, 40)
        assert offer_1_stock_1.bookingLimitDatetime == datetime.datetime(2023, 9, 26, 8, 40)
        assert offer_1_stock_1.features == ["VF", "ICE"]
        assert offer_1_stock_1.quantity == 147
        assert offer_1_stock_1.price == decimal.Decimal("12.0")
        assert offer_1_stock_1.priceCategory.price == decimal.Decimal("12.0")
        assert offer_1_stock_1.priceCategory.label == "PASS CULTURE"

        assert len(offer_2.activeStocks) == 2
        offer_2_stocks = offer_2.activeStocks
        offer_2_stocks.sort(key=lambda offer: offer.idAtProviders)
        offer_2_stock_1 = offer_2_stocks[0]
        assert offer_2_stock_1.idAtProviders == f"145%{venue_id}%Boost#15978"
        assert offer_2_stock_1.beginningDatetime == datetime.datetime(2023, 9, 26, 12, 20)
        assert offer_2_stock_1.bookingLimitDatetime == datetime.datetime(2023, 9, 26, 12, 20)
        assert offer_2_stock_1.features == ["VF", "ICE"]
        assert offer_2_stock_1.quantity == 152
        assert offer_2_stock_1.price == decimal.Decimal("12.0")
        assert offer_2_stock_1.priceCategory.price == decimal.Decimal("12.0")
        assert offer_2_stock_1.priceCategory.label == "PASS CULTURE"

        offer_2_stock_2 = offer_2_stocks[1]
        assert offer_2_stock_2.idAtProviders == f"145%{venue_id}%Boost#16277"
        assert offer_2_stock_2.beginningDatetime == datetime.datetime(2023, 9, 26, 9, 10)
        assert offer_2_stock_2.bookingLimitDatetime == datetime.datetime(2023, 9, 26, 9, 10)
        assert offer_2_stock_2.features == ["VO"]
        assert offer_2_stock_2.quantity == 452
        assert offer_2_stock_2.price == decimal.Decimal("6.0")
        assert offer_2_stock_2.priceCategory.price == decimal.Decimal("6.0")
        assert offer_2_stock_2.priceCategory.label == "PASS CULTURE"

        assert len(products_with_poster) == 2
        product_1, poster_url_1 = products_with_poster[0]
        product_2, poster_url_2 = products_with_poster[1]

        assert product_1 == offer_1.product
        assert poster_url_1 == "http://example.com/images/159673.jpg"
        assert product_2 == offer_2.product
        assert poster_url_2 == "http://example.com/images/159570.jpg"

    @time_machine.travel(datetime.datetime(2023, 8, 12, 12, 41, 30), tick=False)
    @mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date")
    def test_load_should_update_product_offer_and_stocks(self, update_finance_event_pricing_date_mock, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        offer_1 = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            idAtProvider=f"161%{venue_id}%Boost",
            publicationDatetime=datetime.datetime(2023, 7, 10, 10, 0, 15),
            name="MISSION IMPOSSIBLE quelque chose de dead",
            lastProvider=venue_provider.provider,
        )
        stock_1 = offers_factories.EventStockFactory(
            beginningDatetime=datetime.datetime(2023, 9, 25, 7, 30),
            bookingLimitDatetime=datetime.datetime(2023, 9, 25, 7, 30),
            offer=offer_1,
            priceCategory__priceCategoryLabel__label="PCU",
            priceCategory__price=Decimal("5.0"),
            price=Decimal("5.0"),
            lastProvider=venue_provider.provider,
            idAtProviders=f"161%{venue_id}%Boost#15971",
        )
        bookings_factories.BookingFactory(stock=stock_1)

        self.setup_requests_mock(requests_mock)

        etl_process = BoostExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        transform_result = etl_process._transform(extract_result=extract_result)
        offers_id, _ = etl_process._load(transform_result)

        assert len(db.session.query(offers_models.Offer).all()) == 2

        offer_2 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"145%{venue_id}%Boost").one_or_none()

        assert offers_id == set([offer_1.id, offer_2.id])
        assert offer_1
        assert offer_1.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_1.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_1.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_1.publicationDatetime == datetime.datetime(2023, 7, 10, 10, 0, 15)  # should not have changed
        assert offer_1.name == "MISSION IMPOSSIBLE DEAD RECKONING PARTIE 1"

        assert offer_1.product
        assert offer_1.product.name == "MISSION IMPOSSIBLE DEAD RECKONING PARTIE 1"
        assert offer_1.product.durationMinutes == 163
        assert offer_1.product.extraData["allocineId"] == 270935
        assert offer_1.product.extraData["visa"] == "159673"

        assert offers_id == set([offer_1.id, offer_2.id])

        assert len(db.session.query(offers_models.Stock).all()) == 3

        assert len(offer_1.activeStocks) == 1
        assert offer_1.activeStocks[0] == stock_1

        assert stock_1.idAtProviders == f"161%{venue_id}%Boost#15971"
        assert stock_1.beginningDatetime == datetime.datetime(2023, 9, 26, 8, 40)
        assert stock_1.bookingLimitDatetime == datetime.datetime(2023, 9, 26, 8, 40)
        assert stock_1.features == ["VF", "ICE"]
        assert stock_1.quantity == 148  # bookedQuantity +remaining
        assert stock_1.price == decimal.Decimal("12.0")
        assert stock_1.priceCategory.price == decimal.Decimal("12.0")
        assert stock_1.priceCategory.label == "PASS CULTURE"
        # should have been called because beginningDatetime has changed
        update_finance_event_pricing_date_mock.assert_called_once_with(stock_1)

    @time_machine.travel(datetime.datetime(2023, 8, 12, 12, 41, 30), tick=False)
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_execute_should_create_and_index_offer(self, async_index_offer_ids_mock, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        file_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            poster_mission_impossible = thumb_file.read()
        requests_mock.get("http://example.com/images/159673.jpg", content=poster_mission_impossible)
        requests_mock.get("http://example.com/images/159570.jpg", exc=requests.exceptions.ConnectTimeout)  # huho

        BoostExtractTransformLoadProcess(venue_provider).execute()

        offer_1 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"161%{venue_id}%Boost").one_or_none()
        offer_2 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"145%{venue_id}%Boost").one_or_none()

        assert offer_1
        assert offer_1.idAtProvider == f"161%{venue_id}%Boost"
        assert offer_1.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_1.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_1.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_1.publicationDatetime == datetime.datetime(2023, 8, 12, 12, 41, 30)
        assert offer_1.dateModifiedAtLastProvider == datetime.datetime(2023, 8, 12, 12, 41, 30, tzinfo=datetime.UTC)

        assert offer_1.product
        assert offer_1.product.name == "MISSION IMPOSSIBLE DEAD RECKONING PARTIE 1"
        assert offer_1.product.durationMinutes == 163
        assert offer_1.product.extraData["allocineId"] == 270935
        assert offer_1.product.extraData["visa"] == "159673"
        assert len(offer_1.product.productMediations) == 1
        assert offer_1.product.productMediations[0].lastProvider == venue_provider.provider
        assert offer_1.product.productMediations[0].imageType == offers_models.ImageType.POSTER

        assert offer_2
        assert offer_2.idAtProvider == f"145%{venue_id}%Boost"
        assert offer_2.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_2.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_2.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_2.publicationDatetime == datetime.datetime(2023, 8, 12, 12, 41, 30)
        assert offer_2.dateModifiedAtLastProvider == datetime.datetime(2023, 8, 12, 12, 41, 30, tzinfo=datetime.UTC)

        assert offer_2.product
        assert offer_2.product.name == "SPIDER-MAN ACROSS THE SPIDER-VERSE"
        assert offer_2.product.durationMinutes == 140
        assert offer_2.product.extraData["allocineId"] == 269975
        assert offer_2.product.extraData["visa"] == "159570"
        assert not offer_2.product.productMediations

        offer_1_stocks = offer_1.activeStocks
        assert len(offer_1_stocks) == 1
        offer_1_stock_1 = offer_1_stocks[0]
        assert offer_1_stock_1.idAtProviders == f"161%{venue_id}%Boost#15971"
        assert offer_1_stock_1.beginningDatetime == datetime.datetime(2023, 9, 26, 8, 40)
        assert offer_1_stock_1.bookingLimitDatetime == datetime.datetime(2023, 9, 26, 8, 40)
        assert offer_1_stock_1.dateModifiedAtLastProvider == datetime.datetime(2023, 8, 12, 12, 41, 30)
        assert offer_1_stock_1.features == ["VF", "ICE"]
        assert offer_1_stock_1.quantity == 147
        assert offer_1_stock_1.price == decimal.Decimal("12.0")
        assert offer_1_stock_1.priceCategory.price == decimal.Decimal("12.0")
        assert offer_1_stock_1.priceCategory.label == "PASS CULTURE"

        assert len(offer_2.activeStocks) == 2
        offer_2_stocks = offer_2.activeStocks
        offer_2_stocks.sort(key=lambda offer: offer.idAtProviders)
        offer_2_stock_1 = offer_2_stocks[0]
        assert offer_2_stock_1.idAtProviders == f"145%{venue_id}%Boost#15978"
        assert offer_2_stock_1.beginningDatetime == datetime.datetime(2023, 9, 26, 12, 20)
        assert offer_2_stock_1.bookingLimitDatetime == datetime.datetime(2023, 9, 26, 12, 20)
        assert offer_2_stock_1.dateModifiedAtLastProvider == datetime.datetime(2023, 8, 12, 12, 41, 30)
        assert offer_2_stock_1.features == ["VF", "ICE"]
        assert offer_2_stock_1.quantity == 152
        assert offer_2_stock_1.price == decimal.Decimal("12.0")
        assert offer_2_stock_1.priceCategory.price == decimal.Decimal("12.0")
        assert offer_2_stock_1.priceCategory.label == "PASS CULTURE"

        offer_2_stock_2 = offer_2_stocks[1]
        assert offer_2_stock_2.idAtProviders == f"145%{venue_id}%Boost#16277"
        assert offer_2_stock_2.beginningDatetime == datetime.datetime(2023, 9, 26, 9, 10)
        assert offer_2_stock_2.bookingLimitDatetime == datetime.datetime(2023, 9, 26, 9, 10)
        assert offer_2_stock_2.dateModifiedAtLastProvider == datetime.datetime(2023, 8, 12, 12, 41, 30)
        assert offer_2_stock_2.features == ["VO"]
        assert offer_2_stock_2.quantity == 452
        assert offer_2_stock_2.price == decimal.Decimal("6.0")
        assert offer_2_stock_2.priceCategory.price == decimal.Decimal("6.0")
        assert offer_2_stock_2.priceCategory.label == "PASS CULTURE"

        async_index_offer_ids_mock.assert_called_once_with(
            set([offer_1.id, offer_2.id]),
            reason=search_models.IndexationReason.STOCK_UPDATE,
            log_extra={
                "source": "provider_api",
                "venue_id": venue_provider.venueId,
                "provider_id": venue_provider.providerId,
            },
        )

    def test_should_reuse_price_category(self, requests_mock):
        venue_provider = self.setup_cinema_objects()

        get_cinema_attr_adapter = requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs", json=fixtures.CinemasAttributsEndPointResponse.DATA
        )

        requests_mock.get(
            f"https://cinema-0.example.com/api/showtimes/between/{TODAY_STR}/{FUTURE_DATE_STR}?page=1&per_page=30",
            json=fixtures.ShowtimesEndpointResponse.ONE_FILM_PAGE_1_JSON_DATA,
        )
        requests_mock.get("http://example.com/images/158026.jpg", content=bytes())

        BoostExtractTransformLoadProcess(venue_provider).execute()
        BoostExtractTransformLoadProcess(venue_provider).execute()

        created_price_category = db.session.query(offers_models.PriceCategory).one()
        assert created_price_category.price == decimal.Decimal("6.9")
        assert db.session.query(offers_models.PriceCategoryLabel).count() == 1

        assert get_cinema_attr_adapter.call_count == 2
