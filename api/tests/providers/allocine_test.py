import logging
from unittest.mock import patch

import pytest

from pcapi.connectors.api_allocine import ALLOCINE_API_URL
from pcapi.connectors.api_allocine import AllocineException
from pcapi.connectors.serialization import allocine_serializers
from pcapi.core.offers.models import Product
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers.allocine import get_movie_list
from pcapi.core.providers.allocine import get_movie_poster
from pcapi.core.providers.allocine import get_movies_showtimes
from pcapi.core.providers.allocine import synchronize_products
from pcapi.core.providers.models import Provider

from tests.domain import fixtures


@pytest.mark.usefixtures("db_session")
class AllocineMovieListTest:
    def _configure_api_responses(self, requests_mock):
        requests_mock.get(f"{ALLOCINE_API_URL}/movieList?after=", json=fixtures.ALLOCINE_MOVIE_LIST_PAGE_1)
        requests_mock.get(
            f"{ALLOCINE_API_URL}/movieList?after=YXJyYXljb25uZWN0aW9uOjQ5",
            json=fixtures.ALLOCINE_MOVIE_LIST_PAGE_2,
        )

    def test_synchronize_products_creates_products(self, requests_mock):
        # Given
        self._configure_api_responses(requests_mock)
        assert Product.query.count() == 0

        # When
        synchronize_products()

        # Then
        catalogue = Product.query.order_by(Product.id).all()
        assert len(catalogue) == 5

        allocine_products_provider = Provider.query.filter(
            Provider.name == providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME
        ).one()
        assert all(product.lastProviderId == allocine_products_provider.id for product in catalogue)
        assert all(
            product.idAtProviders == f"{allocine_products_provider.id}:{product.extraData['allocineId']}"
            for product in catalogue
        )

        movie_data = catalogue[0].extraData
        expected_data = fixtures.ALLOCINE_MOVIE_LIST_PAGE_1["movieList"]["edges"][0]["node"]
        assert movie_data["allocineId"] == expected_data["internalId"]
        assert movie_data["backlink"] == expected_data["backlink"]["url"]
        assert movie_data["cast"] == [
            f"{item['node']['actor']['firstName']} {item['node']['actor']['lastName']}"
            for item in expected_data["cast"]["edges"]
        ]
        assert movie_data["companies"] == [
            {"activity": company["activity"], "name": company["company"]["name"]}
            for company in expected_data["companies"]
        ]
        assert movie_data["countries"] == [country["name"] for country in expected_data["countries"]]
        assert movie_data["credits"] == [expected_data["credits"]["edges"][0]["node"]]
        assert movie_data["eidr"] == expected_data["data"]["eidr"]
        assert movie_data["productionYear"] == expected_data["data"]["productionYear"]
        assert "diffusionVersion" not in movie_data
        assert movie_data["genres"] == expected_data["genres"]
        assert movie_data["originalTitle"] == expected_data["originalTitle"]
        assert movie_data["posterUrl"] == expected_data["poster"]["url"]
        assert movie_data["releaseDate"] == expected_data["releases"][0]["releaseDate"]["date"]
        assert movie_data["runtime"] == 21
        assert movie_data["synopsis"] == expected_data["synopsis"]
        assert "theater" not in movie_data
        assert movie_data["title"] == expected_data["title"]
        assert movie_data["type"] == expected_data["type"]

    def test_synchronize_products_updates_products(self, requests_mock):
        # Given
        self._configure_api_responses(requests_mock)
        assert Product.query.count() == 0
        synchronize_products()
        requests_mock.get(f"{ALLOCINE_API_URL}/movieList?after=", json=fixtures.ALLOCINE_MOVIE_LIST_PAGE_1_UPDATED)

        # When
        synchronize_products()

        # Then
        updated_product = Product.query.order_by(Product.id).first()
        assert updated_product.extraData["title"] == "Nouveau titre pour ceux de chez nous"

    def test_synchronize_products_is_idempotent(self, requests_mock):
        # Given
        self._configure_api_responses(requests_mock)
        assert Product.query.count() == 0

        # When
        synchronize_products()
        old_catalogue = Product.query.order_by(Product.id).all()
        synchronize_products()
        new_catalogue = Product.query.order_by(Product.id).all()

        # Then
        assert all(new_product.__dict__ == old_catalogue[idx].__dict__ for idx, new_product in enumerate(new_catalogue))


class GetMovieListFromAllocineTest:
    def _configure_api_responses(self, requests_mock):
        requests_mock.get(
            f"{ALLOCINE_API_URL}/movieList?after=",
            json=fixtures.ALLOCINE_MOVIE_LIST_PAGE_1,
        )
        requests_mock.get(
            f"{ALLOCINE_API_URL}/movieList?after=YXJyYXljb25uZWN0aW9uOjQ5",
            json=fixtures.ALLOCINE_MOVIE_LIST_PAGE_2,
        )

    def test_get_all_pages(self, requests_mock):
        self._configure_api_responses(requests_mock)
        movies = get_movie_list()
        assert len(movies) == 5
        assert movies[0].internalId == 131136
        assert movies[1].internalId == 41324
        assert movies[2].internalId == 2161
        assert movies[3].internalId == 4076
        assert movies[4].internalId == 325691

    @patch("pcapi.connectors.api_allocine.get_movie_list_page")
    def test_handles_api_exception(self, mock_get_movie_list_page, caplog):
        mock_get_movie_list_page.side_effect = AllocineException("API call failed")
        with caplog.at_level(logging.ERROR):
            get_movie_list()

        assert caplog.messages[0] == "Could not get movies page at cursor ''. Error: 'API call failed'"


class GetMovieShowtimeListFromAllocineTest:
    def setup_method(self):
        self.theater_id = "123456789"

    @patch("pcapi.core.providers.allocine.api_allocine.get_movies_showtimes_from_allocine")
    def test_should_exclude_empty_movies_and_special_events(self, mock_get_movies_showtimes):
        # Given
        mock_get_movies_showtimes.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )

        # When
        movie_showtimes = get_movies_showtimes(self.theater_id)

        # Then
        mock_get_movies_showtimes.assert_called_once_with(self.theater_id)
        assert next(movie_showtimes).movie.internalId == 131136
        assert next(movie_showtimes, None) is None

    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    def test_handles_api_exception(self, mock_get_movie_list_page, caplog):
        mock_get_movie_list_page.side_effect = AllocineException("API call failed")
        with caplog.at_level(logging.ERROR):
            get_movies_showtimes(self.theater_id)

        assert (
            caplog.messages[0]
            == f"Could not get movies showtimes for theater {self.theater_id}. Error: 'API call failed'"
        )


class GetMoviePosterTest:
    def test_call_allocine_api_with_correct_poster_url(self, requests_mock):
        url = "https://allocine.example.com/movie/poster.jpg"
        requests_mock.get(url, content=b"poster data")
        assert get_movie_poster(url) == b"poster data"

    def test_handle_error_on_movie_poster(self, requests_mock):
        url = "https://allocine.example.com/movie/poster.jpg"
        requests_mock.get(url, status_code=404)
        assert get_movie_poster(url) == b""
