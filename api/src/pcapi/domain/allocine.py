import logging
from typing import Iterator

from pcapi.connectors import api_allocine
from pcapi.connectors.serialization import allocine_serializers


logger = logging.getLogger(__name__)


MOVIE_SPECIAL_EVENT = "SPECIAL_EVENT"


def get_movie_list() -> list[allocine_serializers.AllocineMovie]:
    movie_list = []
    has_next_page = True
    end_cursor = ""
    while has_next_page:
        response = api_allocine.get_movie_list_page(end_cursor)
        movie_list += response.movieList.movies
        end_cursor = response.movieList.pageInfo.endCursor
        has_next_page = response.movieList.pageInfo.hasNextPage

    return movie_list


def get_movies_showtimes(theater_id: str) -> Iterator:
    api_response = api_allocine.get_movies_showtimes_from_allocine(theater_id)
    movies_showtimes = api_response["movieShowtimeList"]["edges"]
    movies_number = api_response["movieShowtimeList"]["totalCount"]
    cleared_movies = _ignore_empty_movies(movies_showtimes)
    filtered_movies_showtimes = _exclude_movie_showtimes_with_special_event_type(cleared_movies)

    logger.info("[ALLOCINE] Total : %s movies", movies_number)

    return iter(filtered_movies_showtimes)


def get_movie_poster(poster_url: str) -> bytes:
    try:
        return api_allocine.get_movie_poster_from_allocine(poster_url)
    except api_allocine.AllocineException:
        logger.info(
            "Could not fetch movie poster",
            extra={
                "provider": "allociné",
                "url": poster_url,
            },
        )
        return bytes()


def _ignore_empty_movies(movies_showtime: list) -> list:
    return list(filter(lambda movie_showtime: movie_showtime["node"].get("movie"), movies_showtime))


def _exclude_movie_showtimes_with_special_event_type(movies_showtime: list) -> list:
    return list(
        filter(lambda movie_showtime: movie_showtime["node"]["movie"]["type"] != MOVIE_SPECIAL_EVENT, movies_showtime)
    )
