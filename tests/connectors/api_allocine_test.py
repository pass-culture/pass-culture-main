from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors.api_allocine import AllocineException
from pcapi.connectors.api_allocine import get_movie_poster_from_allocine
from pcapi.connectors.api_allocine import get_movies_showtimes_from_allocine


class GetMovieShowtimeListTest:
    @patch("pcapi.connectors.api_allocine.requests.get")
    def test_should_return_request_response_from_api(self, request_get):
        # Given
        token = "test"
        theater_id = "test_id"
        expected_result = {"toto"}
        response_return_value = MagicMock(status_code=200, text="")
        response_return_value.json = MagicMock(return_value=expected_result)
        request_get.return_value = response_return_value

        # When
        api_response = get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        request_get.assert_called_once_with(
            f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?" f"token={token}&theater={theater_id}"
        )
        assert api_response == expected_result

    @patch("pcapi.connectors.api_allocine.requests.get")
    def test_should_raise_exception_when_api_call_fails(self, request_get):
        # Given
        token = "test"
        theater_id = "test_id"
        response_return_value = MagicMock(status_code=400, text="")
        response_return_value.json = MagicMock(return_value={})
        request_get.return_value = response_return_value

        # When
        with pytest.raises(AllocineException) as exception:
            get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        assert str(exception.value) == "Error getting API Allocine DATA for theater test_id"

    @patch("pcapi.connectors.api_allocine.requests.get", side_effect=Exception)
    def test_should_raise_exception_when_api_call_fails_with_connection_error(self, mocked_requests_get):
        # Given
        token = "test"
        theater_id = "test_id"

        # When
        with pytest.raises(AllocineException) as allocine_exception:
            get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        assert str(allocine_exception.value) == "Error connecting Allocine API for theater test_id"


class GetMoviePosterFromAllocineTest:
    @patch("pcapi.connectors.api_allocine.requests.get")
    def test_should_return_poster_content_from_allocine_api(self, request_get):
        # Given
        poster_url = "https://fr.web.img6.acsta.net/pictures/19/10/23/15/11/3506165.jpg"
        response_return_value = MagicMock(status_code=200, text="")
        response_return_value.content = bytes()
        request_get.return_value = response_return_value

        # When
        api_response = get_movie_poster_from_allocine(poster_url)

        # Then
        request_get.assert_called_once_with(poster_url)
        assert api_response == bytes()

    @patch("pcapi.connectors.api_allocine.requests.get")
    def test_should_raise_exception_when_allocine_api_call_fails(self, request_get):
        # Given
        poster_url = "https://fr.web.img6.acsta.net/pictures/19/10/23/15/11/3506165.jpg"
        response_return_value = MagicMock(status_code=400, text="")
        response_return_value.content = bytes()
        request_get.return_value = response_return_value

        # When
        with pytest.raises(AllocineException) as exception:
            get_movie_poster_from_allocine(poster_url)

        # Then
        assert (
            str(exception.value) == "Error getting API Allocine movie poster"
            " https://fr.web.img6.acsta.net/pictures/19/10/23/15/11/3506165.jpg"
            " with code 400"
        )
