from unittest.mock import patch, MagicMock

import pytest

from connectors.api_allocine import get_movies_showtimes_list, AllocineException


class GetMovieShowtimeListTest:
    @patch('connectors.api_allocine.requests.get')
    def test_should_return_request_response_from_api(self, request_get):
        # Given
        token = 'test'
        theater_id = 'test_id'
        expected_result = {'toto'}
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(return_value=expected_result)
        request_get.return_value = response_return_value

        # When
        api_response = get_movies_showtimes_list(token, theater_id)

        # Then
        request_get.assert_called_once_with(f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?"
                                            f"token={token}&theater={theater_id}")
        assert api_response == expected_result

    @patch('connectors.api_allocine.requests.get')
    def test_should_raise_exception_when_api_call_fail(self, request_get):
        # Given
        token = 'test'
        theater_id = 'test_id'
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock(return_value={})
        request_get.return_value = response_return_value

        # When
        with pytest.raises(AllocineException) as exception:
            get_movies_showtimes_list(token, theater_id)

        # Then
        assert str(
            exception.value) == "Error getting API Allocine DATA for theater test_id"
