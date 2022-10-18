import datetime

import pytest

from pcapi.connectors.serialization import boost_serializers
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.models import Movie
import pcapi.core.providers.factories as providers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class GetVenueMoviesTest:
    def test_should_return_movies_information(self, requests_mock):
        page_1_json_data = {
            "data": [
                {
                    "id": 52,
                    "titleCnc": "#JESUISLA",
                    "numVisa": 147956,
                    "posterUrl": "http://example.com/images/147956.jpg",
                    "thumbUrl": "http://example.com/img/thumb/film/147956.jpg",
                    "idFilmAllocine": 267615,
                },
                {
                    "id": 62,
                    "titleCnc": "10 JOURS SANS MAMAN",
                    "numVisa": 151172,
                    "posterUrl": "http://example.com/images/151172.jpg",
                    "thumbUrl": "http://example.com/img/thumb/film/151172.jpg",
                    "idFilmAllocine": 273882,
                },
            ],
            "message": "OK",
            "page": 1,
            "previousPage": 1,
            "nextPage": 2,
            "totalPages": 2,
            "totalCount": 4,
        }

        page_2_json_data = {
            "data": [
                {
                    "id": 134,
                    "titleCnc": "100 % LOUP",
                    "numVisa": 2020002189,
                    "posterUrl": "http://example.com/images/2020002189.jpg",
                    "thumbUrl": "http://example.com/img/thumb/film/2020002189.jpg",
                    "idFilmAllocine": 264648,
                },
                {
                    "id": 40,
                    "titleCnc": "1917",
                    "numVisa": 152284,
                    "posterUrl": "http://example.com/images/152284.jpg",
                    "thumbUrl": "http://example.com/img/thumb/film/152284.jpg",
                    "idFilmAllocine": 265567,
                },
            ],
            "message": "OK",
            "page": 2,
            "previousPage": 1,
            "nextPage": 2,
            "totalPages": 2,
            "totalCount": 4,
        }

        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get("https://cinema-0.example.com/films?page=1&per_page=2", json=page_1_json_data)
        requests_mock.get("https://cinema-0.example.com/films?page=2&per_page=2", json=page_2_json_data)
        boost = BoostClientAPI(cinema_str_id)
        movies = boost.get_venue_movies(per_page=2)

        assert movies == [
            Movie(
                id="52",
                title="#JESUISLA",
                duration=1,
                description="",
                posterpath="http://example.com/images/147956.jpg",
                visa="147956",
            ),
            Movie(
                id="62",
                title="10 JOURS SANS MAMAN",
                duration=1,
                description="",
                posterpath="http://example.com/images/151172.jpg",
                visa="151172",
            ),
            Movie(
                id="134",
                title="100 % LOUP",
                duration=1,
                description="",
                posterpath="http://example.com/images/2020002189.jpg",
                visa="2020002189",
            ),
            Movie(
                id="40",
                title="1917",
                duration=1,
                description="",
                posterpath="http://example.com/images/152284.jpg",
                visa="152284",
            ),
        ]


class GetShowtimesTest:
    def test_should_return_showtimes(self, requests_mock):
        page_1_json_data = {
            "data": [
                {
                    "id": 34709,
                    "showDate": "2022-10-17T09:00:00+02:00",
                    "showEndDate": "2022-10-17T12:10:00+02:00",
                    "soldOut": False,
                    "authorizedAccess": False,
                    "numberSeatsRemaining": 136,
                    "film": {
                        "id": 189,
                        "titleCnc": "Avatar : La Voie De L'eau",
                        "numVisa": 123456,
                        "posterUrl": "http://example.com/images/Tmpd188acaa73008cd5bb4f182a82cd3f36.jpg",
                        "thumbUrl": "http://example.com/img/thumb/film/Tmpd188acaa73008cd5bb4f182a82cd3f36.jpg",
                        "idFilmAllocine": 178014,
                    },
                    "format": {"id": 2, "title": "3D"},
                    "version": {"id": 2, "title": "Film Etranger en Langue Etrangère", "code": "VO"},
                    "screen": {
                        "id": 1,
                        "auditoriumNumber": 1,
                        "name": "SALLE CINEMAX",
                        "capacity": 136,
                        "seatingAllowed": False,
                    },
                },
                {
                    "id": 34772,
                    "showDate": "2022-10-17T09:10:00+02:00",
                    "showEndDate": "2022-10-17T11:01:00+02:00",
                    "soldOut": False,
                    "authorizedAccess": False,
                    "numberSeatsRemaining": 136,
                    "film": {
                        "id": 190,
                        "titleCnc": "UNE BELLE COURSE",
                        "numVisa": 153041,
                        "posterUrl": "http://example.com/images/153041.jpg",
                        "thumbUrl": "http://example.com/img/thumb/film/153041.jpg",
                        "idFilmAllocine": 292290,
                    },
                    "format": {"id": 1, "title": "2D"},
                    "version": {"id": 1, "title": "Film Français", "code": "VF"},
                    "screen": {
                        "id": 3,
                        "auditoriumNumber": 3,
                        "name": "SALLE 03",
                        "capacity": 136,
                        "seatingAllowed": True,
                    },
                },
            ],
            "message": "OK",
            "page": 1,
            "previousPage": 1,
            "nextPage": 2,
            "totalPages": 2,
            "totalCount": 4,
        }
        page_2_json_data = {
            "data": [
                {
                    "id": 34877,
                    "showDate": "2022-10-17T09:30:00+02:00",
                    "showEndDate": "2022-10-17T11:26:00+02:00",
                    "soldOut": False,
                    "authorizedAccess": False,
                    "numberSeatsRemaining": 177,
                    "film": {
                        "id": 192,
                        "titleCnc": "JACK MIMOUN ET LES SECRETS DE VAL VERDE",
                        "numVisa": 155104,
                        "posterUrl": "http://example.com/images/155104.jpg",
                        "thumbUrl": "http://example.com/img/thumb/film/155104.jpg",
                        "idFilmAllocine": 271293,
                    },
                    "format": {"id": 1, "title": "2D"},
                    "version": {"id": 1, "title": "Film Français", "code": "VF"},
                    "screen": {
                        "id": 5,
                        "auditoriumNumber": 5,
                        "name": "SALLE 05",
                        "capacity": 177,
                        "seatingAllowed": True,
                    },
                },
                {
                    "id": 34926,
                    "showDate": "2022-10-17T09:40:00+02:00",
                    "showEndDate": "2022-10-17T11:20:00+02:00",
                    "soldOut": False,
                    "authorizedAccess": False,
                    "numberSeatsRemaining": 174,
                    "film": {
                        "id": 193,
                        "titleCnc": "LE NOUVEAU JOUET",
                        "numVisa": 155775,
                        "posterUrl": "http://example.com/images/155775.jpg",
                        "thumbUrl": "http://example.com/img/thumb/film/155775.jpg",
                        "idFilmAllocine": 286890,
                    },
                    "format": {"id": 1, "title": "2D"},
                    "version": {"id": 1, "title": "Film Français", "code": "VF"},
                    "screen": {
                        "id": 6,
                        "auditoriumNumber": 6,
                        "name": "SALLE 06",
                        "capacity": 174,
                        "seatingAllowed": True,
                    },
                },
            ],
            "message": "OK",
            "page": 2,
            "previousPage": 1,
            "nextPage": 2,
            "totalPages": 2,
            "totalCount": 4,
        }

        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema-0.example.com/")
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        requests_mock.get("https://cinema-0.example.com/showtimes?page=1&per_page=2", json=page_1_json_data)
        requests_mock.get("https://cinema-0.example.com/showtimes?page=2&per_page=2", json=page_2_json_data)
        boost = BoostClientAPI(cinema_str_id)
        showtimes = boost.get_showtimes(per_page=2)
        assert showtimes == [
            boost_serializers.ShowTime3(
                id=34709,
                showDate=datetime.datetime(2022, 10, 17, 7, 0),
                showEndDate=datetime.datetime(2022, 10, 17, 10, 10),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=136,
                film=boost_serializers.Film2(
                    id=189,
                    titleCnc="Avatar : La Voie De L'eau",
                    numVisa=123456,
                    posterUrl="http://example.com/images/Tmpd188acaa73008cd5bb4f182a82cd3f36.jpg",
                    thumbUrl="http://example.com/img/thumb/film/Tmpd188acaa73008cd5bb4f182a82cd3f36.jpg",
                    idFilmAllocine=178014,
                ),
                format={"id": 2, "title": "3D"},
                version={"id": 2, "title": "Film Etranger en Langue Etrangère", "code": "VO"},
                screen={
                    "id": 1,
                    "auditoriumNumber": 1,
                    "name": "SALLE CINEMAX",
                    "capacity": 136,
                    "seatingAllowed": False,
                },
            ),
            boost_serializers.ShowTime3(
                id=34772,
                showDate=datetime.datetime(2022, 10, 17, 7, 10),
                showEndDate=datetime.datetime(2022, 10, 17, 9, 1),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=136,
                film=boost_serializers.Film2(
                    id=190,
                    titleCnc="UNE BELLE COURSE",
                    numVisa=153041,
                    posterUrl="http://example.com/images/153041.jpg",
                    thumbUrl="http://example.com/img/thumb/film/153041.jpg",
                    idFilmAllocine=292290,
                ),
                format={"id": 1, "title": "2D"},
                version={"id": 1, "title": "Film Français", "code": "VF"},
                screen={"id": 3, "auditoriumNumber": 3, "name": "SALLE 03", "capacity": 136, "seatingAllowed": True},
            ),
            boost_serializers.ShowTime3(
                id=34877,
                showDate=datetime.datetime(2022, 10, 17, 7, 30),
                showEndDate=datetime.datetime(2022, 10, 17, 9, 26),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=177,
                film=boost_serializers.Film2(
                    id=192,
                    titleCnc="JACK MIMOUN ET LES SECRETS DE VAL VERDE",
                    numVisa=155104,
                    posterUrl="http://example.com/images/155104.jpg",
                    thumbUrl="http://example.com/img/thumb/film/155104.jpg",
                    idFilmAllocine=271293,
                ),
                format={"id": 1, "title": "2D"},
                version={"id": 1, "title": "Film Français", "code": "VF"},
                screen={"id": 5, "auditoriumNumber": 5, "name": "SALLE 05", "capacity": 177, "seatingAllowed": True},
            ),
            boost_serializers.ShowTime3(
                id=34926,
                showDate=datetime.datetime(2022, 10, 17, 7, 40),
                showEndDate=datetime.datetime(2022, 10, 17, 9, 20),
                soldOut=False,
                authorizedAccess=False,
                numberSeatsRemaining=174,
                film=boost_serializers.Film2(
                    id=193,
                    titleCnc="LE NOUVEAU JOUET",
                    numVisa=155775,
                    posterUrl="http://example.com/images/155775.jpg",
                    thumbUrl="http://example.com/img/thumb/film/155775.jpg",
                    idFilmAllocine=286890,
                ),
                format={"id": 1, "title": "2D"},
                version={"id": 1, "title": "Film Français", "code": "VF"},
                screen={"id": 6, "auditoriumNumber": 6, "name": "SALLE 06", "capacity": 174, "seatingAllowed": True},
            ),
        ]
