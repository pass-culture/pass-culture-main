import logging
from typing import Callable
from typing import Iterator

from pcapi.connectors import api_allocine


logger = logging.getLogger(__name__)


MOVIE_SPECIAL_EVENT = "SPECIAL_EVENT"


def get_movies_showtimes(
    api_key: str,
    theater_id: str,
    get_movies_showtimes_from_api: Callable = api_allocine.get_movies_showtimes_from_allocine,
) -> Iterator:
    api_response = get_movies_showtimes_from_api(api_key, theater_id)
    movies_showtimes = api_response["movieShowtimeList"]["edges"]
    movies_number = api_response["movieShowtimeList"]["totalCount"]
    cleared_movies = _ignore_empty_movies(movies_showtimes)
    filtered_movies_showtimes = _exclude_movie_showtimes_with_special_event_type(cleared_movies)

    logger.info("[ALLOCINE] Total : %s movies", movies_number)

    return iter(filtered_movies_showtimes)


def get_movie_poster(
    poster_url: str, get_movie_poster_from_api: Callable = api_allocine.get_movie_poster_from_allocine
) -> bytes:
    try:
        return get_movie_poster_from_api(poster_url)
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
