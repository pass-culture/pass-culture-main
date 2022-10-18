import pytest

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
