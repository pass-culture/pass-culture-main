from unittest.mock import patch, \
    MagicMock

import pytest

from pcapi.connectors.api_allocine import get_movies_showtimes_from_allocine, \
    AllocineException, \
    get_movie_poster_from_allocine


class GetMovieShowtimeListTest:
    @patch('pcapi.connectors.api_allocine.requests.get')
    def test_should_return_request_response_from_api(self, request_get):
        # Given
        token = 'test'
        theater_id = 'test_id'
        expected_result = {'toto'}
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(return_value=expected_result)
        request_get.return_value = response_return_value

        # When
        api_response = get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        request_get.assert_called_once_with(f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?"
                                            f"token={token}&theater={theater_id}")
        assert api_response == expected_result

    @patch('pcapi.connectors.api_allocine.requests.get')
    def test_should_raise_exception_when_api_call_fails(self, request_get):
        # Given
        token = 'test'
        theater_id = 'test_id'
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock(return_value={})
        request_get.return_value = response_return_value

        # When
        with pytest.raises(AllocineException) as exception:
            get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        assert str(exception.value) == "Error getting API Allocine DATA for theater test_id"

    @patch('pcapi.connectors.api_allocine.requests.get', side_effect=Exception)
    def test_should_raise_exception_when_api_call_fails_with_connection_error(self, mocked_requests_get):
        # Given
        token = 'test'
        theater_id = 'test_id'

        # When
        with pytest.raises(AllocineException) as allocine_exception:
            get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        assert str(allocine_exception.value) == "Error connecting Allocine API for theater test_id"

    @patch('pcapi.connectors.api_allocine.json_logger.info')
    @patch('pcapi.connectors.api_allocine.requests.get')
    def test_tracks_calls_to_allocine_movies_showtimes(self, mocked_requests_get, json_logger_info):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(return_value={})
        mocked_requests_get.return_value = response_return_value
        token = 'test'
        theater_id = 'test_id'

        # When
        get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        json_logger_info.assert_called_once()
        json_logger_info.assert_called_with("Loading movie showtimes from Allocine",
                                            extra={'theater': theater_id, 'service': 'ApiAllocine'})

    @patch('pcapi.connectors.api_allocine.json_logger.error')
    @patch('pcapi.connectors.api_allocine.requests.get', side_effect=Exception)
    def test_tracks_api_connection_failure(self, mocked_requests_get, json_logger_error):
        # Given
        token = 'test'
        theater_id = 'test_id'

        # When
        with pytest.raises(AllocineException):
            get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        json_logger_error.assert_called_once()
        json_logger_error.assert_called_with("Error connecting to Allocine API",
                                             extra={'theater': theater_id, 'service': 'ApiAllocine'})

    @patch('pcapi.connectors.api_allocine.json_logger.error')
    @patch('pcapi.connectors.api_allocine.requests.get')
    def test_tracks_api_request_failure(self, request_get, json_logger_error):
        # Given
        token = 'test'
        theater_id = 'test_id'
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock(return_value={})
        request_get.return_value = response_return_value

        # When
        with pytest.raises(AllocineException):
            get_movies_showtimes_from_allocine(token, theater_id)

        # Then
        json_logger_error.assert_called_once()
        json_logger_error.assert_called_with("Error in request to Allocine API",
                                             extra={'theater': theater_id, 'service': 'ApiAllocine'})


class GetMoviePosterFromAllocineTest:
    @patch('pcapi.connectors.api_allocine.requests.get')
    def test_should_return_poster_content_from_allocine_api(self, request_get):
        # Given
        poster_url = 'https://fr.web.img6.acsta.net/pictures/19/10/23/15/11/3506165.jpg'
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.content = bytes()
        request_get.return_value = response_return_value

        # When
        api_response = get_movie_poster_from_allocine(poster_url)

        # Then
        request_get.assert_called_once_with(poster_url)
        assert api_response == bytes()

    @patch('pcapi.connectors.api_allocine.json_logger.info')
    @patch('pcapi.connectors.api_allocine.requests.get')
    def test_tracks_calls_to_allocine_movie_poster(self, mocked_requests_get, json_logger_info):
        # Given
        poster_url = 'https://fr.web.img6.acsta.net/pictures/19/10/23/15/11/3506165.jpg'
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.content = bytes()
        mocked_requests_get.return_value = response_return_value

        # When
        get_movie_poster_from_allocine(poster_url)

        # Then
        json_logger_info.assert_called_once()
        json_logger_info.assert_called_with("Loading movie poster from Allocine",
                                            extra={'poster': poster_url, 'service': 'ApiAllocine'})

    @patch('pcapi.connectors.api_allocine.requests.get')
    def test_should_raise_exception_when_allocine_api_call_fails(self, request_get):
        # Given
        poster_url = 'https://fr.web.img6.acsta.net/pictures/19/10/23/15/11/3506165.jpg'
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.content = bytes()
        request_get.return_value = response_return_value

        # When
        with pytest.raises(AllocineException) as exception:
            get_movie_poster_from_allocine(poster_url)

        # Then
        assert str(exception.value) == "Error getting API Allocine movie poster" \
                                       " https://fr.web.img6.acsta.net/pictures/19/10/23/15/11/3506165.jpg" \
                                       " with code 400"

    @patch('pcapi.connectors.api_allocine.json_logger.error')
    @patch('pcapi.connectors.api_allocine.requests.get')
    def test_tracks_failed_calls_to_allocine_movie_poster(self, mocked_requests_get, json_logger_error):
        # Given
        poster_url = 'https://fr.web.img6.acsta.net/pictures/19/10/23/15/11/3506165.jpg'
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.content = bytes()
        mocked_requests_get.return_value = response_return_value

        # When
        with pytest.raises(AllocineException):
            get_movie_poster_from_allocine(poster_url)

        # Then
        json_logger_error.assert_called_once()
        json_logger_error.assert_called_with("Failed to load movie poster from Allocine",
                                             extra={'poster': poster_url, 'service': 'ApiAllocine'})
