import datetime
import decimal
import logging
from decimal import Decimal

import pytest

import pcapi.core.offers.models as offers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.core.external_bookings.boost import constants as boost_constants
from pcapi.core.external_bookings.boost import serializers as boost_serializers
from pcapi.core.providers.etls.boost_etl import BoostETLProcess
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.utils import requests

from . import fixtures


pytestmark = pytest.mark.usefixtures("db_session")

TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")
FUTURE_DATE_STR = (datetime.date.today() + datetime.timedelta(days=boost_constants.BOOST_SHOWS_INTERVAL_DAYS)).strftime(
    "%Y-%m-%d"
)


class BoostETLProcessTest:
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

    def test_execute_should_raise_inactive_provider(self):
        venue_provider = self.setup_cinema_objects()
        venue_provider.provider.isActive = False
        etl_process = BoostETLProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveProvider):
            etl_process.execute()

    def test_execute_should_raise_inactive_venue_provider_provider(self):
        venue_provider = self.setup_cinema_objects()
        venue_provider.isActive = False
        etl_process = BoostETLProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveVenueProvider):
            etl_process.execute()

    def test_extract_should_log_and_raise_error(self, caplog, requests_mock):
        venue_provider = self.setup_cinema_objects()
        etl_process = BoostETLProcess(venue_provider)
        requests_mock.get(
            "https://cinema-0.example.com/api/cinemas/attributs",
            exc=requests.exceptions.ConnectTimeout,
        )

        with caplog.at_level(logging.WARNING):
            with pytest.raises(requests.exceptions.ConnectTimeout):
                etl_process.execute()

        assert len(caplog.records) >= 1
        last_record = caplog.records[-1]
        assert last_record.message == "[BoostETLProcess] Step 1 - Extract failed"
        assert last_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {"exc": "ConnectTimeout"},
        }

    def test_extract_should_return_raw_results(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
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

        etl_process = BoostETLProcess(venue_provider)

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

        etl_process = BoostETLProcess(venue_provider)

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
        etl_process = BoostETLProcess(venue_provider)

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
