import copy
from dataclasses import dataclass
import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors.api_allocine import AllocineException
from pcapi.connectors.api_allocine import get_movie_list_page
from pcapi.connectors.api_allocine import get_movie_poster_from_allocine
from pcapi.connectors.api_allocine import get_movies_showtimes_from_allocine
from pcapi.connectors.api_allocine import parse_movie_showtimes
from pcapi.connectors.serialization import allocine_serializers

from tests.connectors import fixtures


@dataclass
class MockedResponse:
    data: dict | list
    status_code: int

    def json(self):
        return self.data


class GetMovieListTest:
    def test_returns_request_response_from_api(self, requests_mock):
        # Given
        expected_result = fixtures.MOVIE_LIST
        requests_mock.get(
            "https://graph-api-proxy.allocine.fr/api/query/movieList?after=",
            json=expected_result,
        )

        # When
        api_response = get_movie_list_page()

        # Then
        assert api_response == allocine_serializers.AllocineMovieListResponse.model_validate(expected_result)

    def test_raises_exception_when_api_call_fails(self, requests_mock):
        # Given
        requests_mock.get(
            "https://graph-api-proxy.allocine.fr/api/query/movieList?after=",
            json={},
            status_code=400,
        )

        # When
        with pytest.raises(AllocineException) as exception:
            get_movie_list_page()

        # Then
        assert str(exception.value) == "Error getting API Allocine data to get movie list, error=400"

    def test_raises_exception_when_api_call_fails_with_connection_error(self, requests_mock):
        requests_mock.get(
            "https://graph-api-proxy.allocine.fr/api/query/movieList?after=",
            exc=Exception,
        )
        # When
        with pytest.raises(AllocineException) as allocine_exception:
            get_movie_list_page()

        # Then
        assert str(allocine_exception.value) == "Error connecting Allocine API to get movie list"

    def test_extracts_allocine_id_from_response(self, requests_mock):
        # Given
        allocine_response = copy.deepcopy(fixtures.MOVIE_LIST)
        allocine_response["movieList"]["edges"][0]["node"]["credits"]["edges"][0]["node"]["person"] = None
        requests_mock.get("https://graph-api-proxy.allocine.fr/api/query/movieList?after=", json=allocine_response)

        # When
        with pytest.raises(AllocineException) as exception:
            get_movie_list_page()

        # Then
        assert str(exception.value).endswith("Allocine Id: 131136")

    def test_doesnt_extract_allocine_id_from_response(self, requests_mock, caplog):
        # Given
        allocine_response = copy.deepcopy(fixtures.MOVIE_LIST)
        del allocine_response["movieList"]["edges"]
        requests_mock.get("https://graph-api-proxy.allocine.fr/api/query/movieList?after=", json=allocine_response)

        # When
        with pytest.raises(AllocineException) as exception:
            with caplog.at_level(logging.ERROR):
                get_movie_list_page()

        # Then
        assert caplog.records[0].message == "Error extracting allocine id from movie list"
        assert str(exception.value).endswith("Allocine Id: None")


class GetMovieShowtimeListTest:
    def test_should_return_request_response_from_api(self, requests_mock):
        # Given
        theater_id = "test_id"
        expected_result = fixtures.MOVIE_SHOWTIME_LIST
        requests_mock.get(
            f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?theater={theater_id}",
            json=expected_result,
        )

        # When
        api_response = get_movies_showtimes_from_allocine(theater_id)

        # Then
        assert api_response == allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(expected_result)

    def test_should_raise_exception_when_api_call_fails(self, requests_mock):
        # Given
        theater_id = "test_id"
        requests_mock.get(
            f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?theater={theater_id}",
            json={},
            status_code=400,
        )

        # When
        with pytest.raises(AllocineException) as exception:
            get_movies_showtimes_from_allocine(theater_id)

        # Then
        assert str(exception.value) == "Error getting API Allocine DATA for theater test_id"

    @patch("pcapi.connectors.api_allocine.requests.get", side_effect=Exception)
    def test_should_raise_exception_when_api_call_fails_with_connection_error(self, mocked_requests_get):
        # Given
        theater_id = "test_id"

        # When
        with pytest.raises(AllocineException) as allocine_exception:
            get_movies_showtimes_from_allocine(theater_id)

        # Then
        assert str(allocine_exception.value) == "Error connecting Allocine API for theater test_id"

    @patch("pcapi.connectors.api_allocine.requests")
    def test_should_drop_invalid_showtimes_and_move_on(self, requests_mock):
        payload = copy.deepcopy(fixtures.MOVIE_SHOWTIME_LIST)

        # add one (valid) edge
        valid_edge = copy.deepcopy(payload["movieShowtimeList"]["edges"][0])
        payload["movieShowtimeList"]["edges"].append(valid_edge)
        # one and only movie becomes invalid because of one showtime language
        payload["movieShowtimeList"]["edges"][0]["node"]["showtimes"][0]["languages"] = [None]

        requests_mock.get.return_value = MockedResponse(data=payload, status_code=200)
        api_response = get_movies_showtimes_from_allocine("does not matter")

        expected_result = copy.deepcopy(fixtures.MOVIE_SHOWTIME_LIST)
        assert api_response == allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(expected_result)


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


def copy_movie_showtime_list():
    return copy.deepcopy(fixtures.MOVIE_SHOWTIME_LIST)


@pytest.fixture(name="json_data")
def json_data_fixture():
    return copy_movie_showtime_list()


class ParseMovieShowtimesTest:
    def test_parse_one_error(self, json_data):
        self.append_valid_edge(json_data)

        # one and only movie becomes invalid because of one showtime language
        json_data["movieShowtimeList"]["edges"][0]["node"]["showtimes"][0]["languages"].append("oops")

        showtimes = parse_movie_showtimes(json_data, theater_id=1)

        expected_result = copy_movie_showtime_list()
        assert showtimes == allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(expected_result)

    def test_parse_no_error(self, json_data):
        showtimes = parse_movie_showtimes(json_data, theater_id=1)

        expected_result = copy.deepcopy(fixtures.MOVIE_SHOWTIME_LIST)
        assert showtimes == allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(expected_result)

    def test_one_error_mixed_with_some_valid_rows(self, json_data):
        self.append_invalid_edge(json_data)
        valid_edge = self.append_valid_edge(json_data)

        showtimes = parse_movie_showtimes(json_data, theater_id=1)

        expected_result = copy_movie_showtime_list()
        expected_result["movieShowtimeList"]["edges"].append(valid_edge)

        assert showtimes == allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(expected_result)

    def test_many_errors_mixed_with_many_valid_rows(self, json_data):
        self.append_invalid_edge(json_data)
        valid_edge1 = self.append_valid_edge(json_data)
        self.append_invalid_edge(json_data)
        valid_edge2 = self.append_valid_edge(json_data)
        self.append_invalid_edge(json_data)

        showtimes = parse_movie_showtimes(json_data, theater_id=1)

        expected_result = copy_movie_showtime_list()
        expected_result["movieShowtimeList"]["edges"].append(valid_edge1)
        expected_result["movieShowtimeList"]["edges"].append(valid_edge2)

        assert showtimes == allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(expected_result)

    def test_starts_with_valid_rows_ends_with_errors(self, json_data):
        valid_edge1 = self.append_valid_edge(json_data)
        valid_edge2 = self.append_valid_edge(json_data)

        self.append_invalid_edge(json_data)
        self.append_invalid_edge(json_data)

        showtimes = parse_movie_showtimes(json_data, theater_id=1)

        expected_result = copy.deepcopy(fixtures.MOVIE_SHOWTIME_LIST)
        expected_result["movieShowtimeList"]["edges"].append(valid_edge1)
        expected_result["movieShowtimeList"]["edges"].append(valid_edge2)

        assert showtimes == allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(expected_result)

    def test_starts_with_errors_ends_with_valid_rows(self, json_data):
        self.append_invalid_edge(json_data)
        self.append_invalid_edge(json_data)

        valid_edge1 = self.append_valid_edge(json_data)
        valid_edge2 = self.append_valid_edge(json_data)

        showtimes = parse_movie_showtimes(copy.deepcopy(json_data), theater_id=1)

        expected_result = copy.deepcopy(fixtures.MOVIE_SHOWTIME_LIST)
        expected_result["movieShowtimeList"]["edges"].append(valid_edge1)
        expected_result["movieShowtimeList"]["edges"].append(valid_edge2)

        assert showtimes == allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(expected_result)

    def append_valid_edge(self, json_data):
        edge = copy.deepcopy(json_data["movieShowtimeList"]["edges"][0])
        json_data["movieShowtimeList"]["edges"].append(edge)

        return edge

    def append_invalid_edge(self, json_data):
        edge = copy.deepcopy(json_data["movieShowtimeList"]["edges"][0])
        edge["node"]["showtimes"][0]["languages"].append("Unknown")

        json_data["movieShowtimeList"]["edges"].append(edge)
