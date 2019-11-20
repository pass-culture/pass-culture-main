from typing import Callable

from connectors.api_allocine import get_movies_showtimes_from_allocine, get_movie_poster_from_allocine
from utils.logger import logger


def get_movies_showtimes(api_key: str, theater_id: str,
                         get_movies_showtimes_from_api: Callable = get_movies_showtimes_from_allocine
                         ) -> iter:
    api_response = get_movies_showtimes_from_api(api_key, theater_id)
    movies_showtimes = api_response["movieShowtimeList"]["edges"]
    movies_number = api_response["movieShowtimeList"]["totalCount"]

    logger.info('[ALLOCINE] Total : %s movies' % movies_number)

    return iter(movies_showtimes)


def get_movie_poster(poster_url: str,
                     get_movie_poster_from_api: Callable = get_movie_poster_from_allocine) -> bytes:
    return get_movie_poster_from_api(poster_url)
