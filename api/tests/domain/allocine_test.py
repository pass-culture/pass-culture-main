from unittest.mock import MagicMock
from unittest.mock import Mock

from pcapi.domain.allocine import _exclude_movie_showtimes_with_special_event_type
from pcapi.domain.allocine import get_movie_poster
from pcapi.domain.allocine import get_movies_showtimes


class GetMovieShowtimeListFromAllocineTest:
    def setup_method(self):
        self.theater_id = "123456789"
        self.token = "AZERTY123/@.,!é"
        self.mock_get_movies_showtimes = Mock()

    def test_should_retrieve_result_from_api_connector_with_token_and_theater_id_parameter(self):
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
        self.mock_get_movies_showtimes.return_value = {"movieShowtimeList": {"totalCount": 1, "edges": movies_list}}

        # When
        get_movies_showtimes(self.token, self.theater_id, get_movies_showtimes_from_api=self.mock_get_movies_showtimes)
        # Then
        self.mock_get_movies_showtimes.assert_called_once_with(self.token, self.theater_id)

    def test_should_extract_movies_from_api_result(self):
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
        self.mock_get_movies_showtimes.return_value = {"movieShowtimeList": {"totalCount": 4, "edges": given_movies}}

        # When
        movies = get_movies_showtimes(
            self.token, self.theater_id, get_movies_showtimes_from_api=self.mock_get_movies_showtimes
        )
        # Then
        assert any(expected_movie == next(movies) for expected_movie in expected_movies)


class GetMoviePosterTest:
    def test_should_call_api_with_correct_poster_url(self):
        # Given
        poster_url = "http://url.com"
        mock_get_movie_poster_from_allocine = MagicMock(return_value=bytes())

        # When
        movie_poster = get_movie_poster(poster_url, get_movie_poster_from_api=mock_get_movie_poster_from_allocine)

        # Then
        mock_get_movie_poster_from_allocine.assert_called_once_with("http://url.com")
        assert movie_poster == bytes()


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
