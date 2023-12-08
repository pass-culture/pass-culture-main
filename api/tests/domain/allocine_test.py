from unittest.mock import patch

from pcapi.connectors.api_allocine import ALLOCINE_API_URL
from pcapi.domain.allocine import _exclude_movie_showtimes_with_special_event_type
from pcapi.domain.allocine import get_movie_list
from pcapi.domain.allocine import get_movie_poster
from pcapi.domain.allocine import get_movies_showtimes

from tests.domain import fixtures


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
        assert len(movies) == 4
        assert movies[0].internalId == 131136
        assert movies[1].internalId == 41324
        assert movies[2].internalId == 2161
        assert movies[3].internalId == 4076


class GetMovieShowtimeListFromAllocineTest:
    def setup_method(self):
        self.theater_id = "123456789"

    @patch("pcapi.domain.allocine.api_allocine.get_movies_showtimes_from_allocine")
    def test_should_retrieve_result_from_api_connector_with_theater_id_parameter(self, mock_get_movies_showtimes):
        # Given
        movies_list = [
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "title": "Les Contes de la m\u00e8re poule",
                        "type": "COMMERCIAL",
                    }
                }
            }
        ]
        mock_get_movies_showtimes.return_value = {"movieShowtimeList": {"totalCount": 1, "edges": movies_list}}

        # When
        get_movies_showtimes(self.theater_id)
        # Then
        mock_get_movies_showtimes.assert_called_once_with(self.theater_id)

    @patch("pcapi.domain.allocine.api_allocine.get_movies_showtimes_from_allocine")
    def test_should_extract_movies_from_api_result(self, mock_get_movies_showtimes):
        # Given
        given_movies = [
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "title": "Les Contes de la m\u00e8re poule",
                        "type": "COMMERCIAL",
                    }
                }
            },
            {"node": {"movie": None}},
            {"node": {}},
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6NTA0MDk=",
                        "internalId": 50609,
                        "title": "Le Ch\u00e2teau ambulant",
                        "type": "BRAND_CONTENT",
                    }
                }
            },
        ]

        expected_movies = [
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "title": "Les Contes de la m\u00e8re poule",
                        "type": "COMMERCIAL",
                    }
                }
            },
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6NTA0MDk=",
                        "internalId": 50609,
                        "title": "Le Ch\u00e2teau ambulant",
                        "type": "BRAND_CONTENT",
                    }
                }
            },
        ]
        mock_get_movies_showtimes.return_value = {"movieShowtimeList": {"totalCount": 4, "edges": given_movies}}

        # When
        movies = get_movies_showtimes(self.theater_id)
        # Then
        assert any(expected_movie == next(movies) for expected_movie in expected_movies)


class GetMoviePosterTest:
    def test_call_allocine_api_with_correct_poster_url(self, requests_mock):
        url = "https://allocine.example.com/movie/poster.jpg"
        requests_mock.get(url, content=b"poster data")
        assert get_movie_poster(url) == b"poster data"

    def test_handle_error_on_movie_poster(self, requests_mock):
        url = "https://allocine.example.com/movie/poster.jpg"
        requests_mock.get(url, status_code=404)
        assert get_movie_poster(url) == b""


class RemoveMovieShowsWithSpecialEventTypeTest:
    def test_should_remove_movie_shows_with_special_event_type(self):
        # Given
        movies_list = [
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "title": "Les Contes de la m\u00e8re poule",
                        "type": "COMMERCIAL",
                    }
                }
            },
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6NTA0MDk=",
                        "internalId": 50609,
                        "title": "Le Ch\u00e2teau ambulant",
                        "type": "SPECIAL_EVENT",
                    }
                }
            },
        ]

        # When
        filtered_movies_list = _exclude_movie_showtimes_with_special_event_type(movies_list)

        # Then
        assert len(filtered_movies_list) == 1
        assert filtered_movies_list == [
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mzc4MzI=",
                        "internalId": 37832,
                        "title": "Les Contes de la m\u00e8re poule",
                        "type": "COMMERCIAL",
                    }
                }
            }
        ]
