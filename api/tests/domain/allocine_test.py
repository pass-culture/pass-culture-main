from unittest.mock import patch

from pcapi.connectors.api_allocine import ALLOCINE_API_URL
from pcapi.connectors.serialization import allocine_serializers
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


class GetMoviePosterTest:
    def test_call_allocine_api_with_correct_poster_url(self, requests_mock):
        url = "https://allocine.example.com/movie/poster.jpg"
        requests_mock.get(url, content=b"poster data")
        assert get_movie_poster(url) == b"poster data"

    def test_handle_error_on_movie_poster(self, requests_mock):
        url = "https://allocine.example.com/movie/poster.jpg"
        requests_mock.get(url, status_code=404)
        assert get_movie_poster(url) == b""
