import logging
from typing import Iterator

import pydantic

from pcapi.connectors.api_allocine import get_movie_list_page
from pcapi.connectors.api_allocine import get_movie_poster_from_allocine
from pcapi.connectors.api_allocine import get_movies_showtimes_from_allocine
from pcapi.connectors.serialization import allocine_serializers


logger = logging.getLogger(__name__)


MOVIE_SPECIAL_EVENT = "SPECIAL_EVENT"


def get_movie_list() -> list[allocine_serializers.AllocineMovie]:
    movie_list = []
    has_next_page = True
    end_cursor = ""
    while has_next_page:
        raw_response = get_movie_list_page(end_cursor)
        response = allocine_serializers.dict_to_obj(raw_response)
        movie_list += response.movieList.movies
        end_cursor = response.movieList.pageInfo.endCursor
        has_next_page = response.movieList.pageInfo.hasNextPage

    return movie_list


def get_movies_showtimes(theater_id: str) -> Iterator:
    api_response = get_movies_showtimes_from_allocine(theater_id)
    movies_showtimes = api_response["movieShowtimeList"]["edges"]
    movies_number = api_response["movieShowtimeList"]["totalCount"]
    cleared_movies = _ignore_empty_movies(movies_showtimes)
    filtered_movies_showtimes = _exclude_movie_showtimes_with_special_event_type(cleared_movies)

    logger.info("[ALLOCINE] Total : %s movies", movies_number)

    return iter(filtered_movies_showtimes)


def get_movie_poster(poster_url: str) -> bytes:
    return get_movie_poster_from_allocine(poster_url)


def _ignore_empty_movies(movies_showtime: list) -> list:
    return list(filter(lambda movie_showtime: movie_showtime["node"].get("movie"), movies_showtime))


def _exclude_movie_showtimes_with_special_event_type(movies_showtime: list) -> list:
    return list(
        filter(lambda movie_showtime: movie_showtime["node"]["movie"]["type"] != MOVIE_SPECIAL_EVENT, movies_showtime)
    )
