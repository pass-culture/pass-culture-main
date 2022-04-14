import logging
from typing import Callable

from pcapi.connectors.api_allocine import get_movie_poster_from_allocine
from pcapi.connectors.api_allocine import get_movies_showtimes_from_allocine


logger = logging.getLogger(__name__)


MOVIE_SPECIAL_EVENT = "SPECIAL_EVENT"


def get_movies_showtimes(
    api_key: str, theater_id: str, get_movies_showtimes_from_api: Callable = get_movies_showtimes_from_allocine
) -> iter:  # type: ignore [valid-type]
    api_response = get_movies_showtimes_from_api(api_key, theater_id)
    movies_showtimes = api_response["movieShowtimeList"]["edges"]
    movies_number = api_response["movieShowtimeList"]["totalCount"]
    cleared_movies = _ignore_empty_movies(movies_showtimes)
    filtered_movies_showtimes = _exclude_movie_showtimes_with_special_event_type(cleared_movies)

    logger.info("[ALLOCINE] Total : %s movies", movies_number)

    return iter(filtered_movies_showtimes)


def get_movie_poster(poster_url: str, get_movie_poster_from_api: Callable = get_movie_poster_from_allocine) -> bytes:
    return get_movie_poster_from_api(poster_url)


def _ignore_empty_movies(movies_showtime: list) -> list:
    return list(filter(lambda movie_showtime: movie_showtime["node"].get("movie"), movies_showtime))


def _exclude_movie_showtimes_with_special_event_type(movies_showtime: list) -> list:
    return list(
        filter(lambda movie_showtime: movie_showtime["node"]["movie"]["type"] != MOVIE_SPECIAL_EVENT, movies_showtime)
    )
