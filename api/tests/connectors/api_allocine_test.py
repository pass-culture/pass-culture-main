from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors.api_allocine import AllocineException
from pcapi.connectors.api_allocine import get_movie_list_page
from pcapi.connectors.api_allocine import get_movie_poster_from_allocine
from pcapi.connectors.api_allocine import get_movies_showtimes_from_allocine
from pcapi.connectors.serialization import allocine_serializers


class GetMovieListTest:
    def should_return_request_response_from_api(self, requests_mock):
        # Given
        expected_result = {
            "movieList": {
                "totalCount": 4,
                "pageInfo": {"hasNextPage": True, "endCursor": "YXJyYXljb25uZWN0aW9uOjQ5"},
                "edges": [
                    {
                        "node": {
                            "id": "TW92aWU6MTMxMTM2",
                            "internalId": 131136,
                            "backlink": {
                                "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=131136.html",
                                "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                            },
                            "data": {"eidr": None, "productionYear": 1915},
                            "title": "Ceux de chez nous",
                            "originalTitle": "Ceux de chez nous",
                            "type": "FEATURE_FILM",
                            "runtime": "PT0H21M0S",
                            "poster": {"url": "https://fr.web.img2.acsta.net/medias/nmedia/18/78/15/02/19447537.jpg"},
                            "synopsis": "Alors que la Premi\u00e8re Guerre Mondiale a \u00e9clat\u00e9, et en r\u00e9ponse aux propos des intellectuels allemands de l'\u00e9poque, Sacha Guitry filme les grands artistes de l'\u00e9poque qui contribuent au rayonnement culturel de la France.",
                            "releases": [
                                {
                                    "name": "ReRelease",
                                    "releaseDate": {"date": "2023-11-01"},
                                    "data": {
                                        "tech": {
                                            "auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [411399]"
                                        },
                                        "visa_number": "108245",
                                    },
                                    "certificate": None,
                                },
                                {
                                    "name": "Released",
                                    "releaseDate": {"date": "1915-11-22"},
                                    "data": {
                                        "tech": {
                                            "auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [411400]"
                                        },
                                        "visa_number": "108245",
                                    },
                                    "certificate": None,
                                },
                            ],
                            "credits": {
                                "edges": [
                                    {
                                        "node": {
                                            "person": {"firstName": "Sacha", "lastName": "Guitry"},
                                            "position": {"name": "DIRECTOR"},
                                        }
                                    }
                                ]
                            },
                            "cast": {
                                "backlink": {
                                    "url": "https://www.allocine.fr/film/fichefilm-131136/casting/",
                                    "label": "Casting complet du film sur AlloCin\u00e9",
                                },
                                "edges": [
                                    {
                                        "node": {
                                            "actor": {"firstName": "Sacha", "lastName": "Guitry"},
                                            "role": "(doublage)",
                                        }
                                    },
                                    {"node": {"actor": {"firstName": "Sarah", "lastName": "Bernhardt"}, "role": None}},
                                    {"node": {"actor": {"firstName": "Anatole", "lastName": "France"}, "role": None}},
                                ],
                            },
                            "countries": [{"name": "France", "alpha3": "FRA"}],
                            "genres": ["DOCUMENTARY"],
                            "companies": [
                                {"activity": "Distribution", "company": {"name": "Les Acacias"}},
                                {"activity": "Distribution", "company": {"name": "Les Acacias"}},
                            ],
                        }
                    },
                    {
                        "node": {
                            "id": "TW92aWU6NDEzMjQ=",
                            "internalId": 41324,
                            "backlink": {
                                "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=41324.html",
                                "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                            },
                            "data": {"eidr": "10.5240/205D-17AD-BBB2-F62A-2481-7", "productionYear": 1931},
                            "title": "The Front page",
                            "originalTitle": "The Front page",
                            "type": "FEATURE_FILM",
                            "runtime": "PT1H41M0S",
                            "poster": {"url": "https://fr.web.img4.acsta.net/pictures/17/12/21/10/23/2878333.jpg"},
                            "synopsis": "Un journaliste s'appr\u00eate \u00e0 se marier, lorsqu'il est envoy\u00e9 de toute urgence sur un scoop: l'ex\u00e9cution d'un homme accus\u00e9 d'avoir tu\u00e9 un policier. Mais ce dernier s'\u00e9vade.",
                            "releases": [
                                {
                                    "name": "ReRelease",
                                    "releaseDate": {"date": "2024-10-16"},
                                    "data": {
                                        "tech": {
                                            "auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [408737]"
                                        }
                                    },
                                    "certificate": None,
                                },
                                {
                                    "name": "Released",
                                    "releaseDate": {"date": "1931-09-25"},
                                    "data": {
                                        "tech": {
                                            "auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [278514]"
                                        }
                                    },
                                    "certificate": None,
                                },
                            ],
                            "credits": {
                                "edges": [
                                    {
                                        "node": {
                                            "person": {"firstName": "Lewis", "lastName": "Milestone"},
                                            "position": {"name": "DIRECTOR"},
                                        }
                                    }
                                ]
                            },
                            "cast": {
                                "backlink": {
                                    "url": "https://www.allocine.fr/film/fichefilm-41324/casting/",
                                    "label": "Casting complet du film sur AlloCin\u00e9",
                                },
                                "edges": [
                                    {
                                        "node": {
                                            "actor": {"firstName": "Adolphe", "lastName": "Menjou"},
                                            "role": "Walter Burns",
                                        }
                                    },
                                    {
                                        "node": {
                                            "actor": {"firstName": "Pat", "lastName": "O'Brien"},
                                            "role": "Hildy Johnson",
                                        }
                                    },
                                    {
                                        "node": {
                                            "actor": {"firstName": "Mary", "lastName": "Brian"},
                                            "role": "Peggy Grant",
                                        }
                                    },
                                ],
                            },
                            "countries": [{"name": "USA", "alpha3": "USA"}],
                            "genres": ["COMEDY"],
                            "companies": [
                                {"activity": "InternationalDistributionExports", "company": {"name": "United Artists"}},
                                {"activity": "Distribution", "company": {"name": "Swashbuckler Films"}},
                                {"activity": "Distribution", "company": {"name": "Swashbuckler Films"}},
                                {"activity": "Production", "company": {"name": "The Caddo company"}},
                            ],
                        }
                    },
                ],
            }
        }

        requests_mock.get(
            "https://graph-api-proxy.allocine.fr/api/query/movieList?after=",
            json=expected_result,
        )

        # When
        api_response = get_movie_list_page()

        # Then
        assert api_response == allocine_serializers.AllocineMovieListResponseAdapter.validate_python(expected_result)

    def test_should_raise_exception_when_api_call_fails(self, requests_mock):
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

    def test_should_raise_exception_when_api_call_fails_with_connection_error(self, requests_mock):
        requests_mock.get(
            "https://graph-api-proxy.allocine.fr/api/query/movieList?after=",
            exc=Exception,
        )
        # When
        with pytest.raises(AllocineException) as allocine_exception:
            get_movie_list_page()

        # Then
        assert str(allocine_exception.value) == "Error connecting Allocine API to get movie list"


class GetMovieShowtimeListTest:
    @patch("pcapi.connectors.api_allocine.requests.get")
    def test_should_return_request_response_from_api(self, request_get):
        # Given
        theater_id = "test_id"
        expected_result = {"toto"}
        response_return_value = MagicMock(status_code=200, text="")
        response_return_value.json = MagicMock(return_value=expected_result)
        request_get.return_value = response_return_value

        # When
        api_response = get_movies_showtimes_from_allocine(theater_id)

        # Then
        request_get.assert_called_once_with(
            f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?theater={theater_id}",
            headers={"Authorization": "Bearer " + settings.ALLOCINE_API_KEY},
        )
        assert api_response == expected_result

    @patch("pcapi.connectors.api_allocine.requests.get")
    def test_should_raise_exception_when_api_call_fails(self, request_get):
        # Given
        theater_id = "test_id"
        response_return_value = MagicMock(status_code=400, text="")
        response_return_value.json = MagicMock(return_value={})
        request_get.return_value = response_return_value

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
