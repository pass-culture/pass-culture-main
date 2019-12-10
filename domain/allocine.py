from typing import Callable

from connectors.api_allocine import get_movies_showtimes_from_allocine, get_movie_poster_from_allocine
from utils.logger import logger

MOVIE_TYPE = 'SPECIAL_EVENT'

def get_movies_showtimes(api_key: str, theater_id: str,
                         get_movies_showtimes_from_api: Callable = get_movies_showtimes_from_allocine
                         ) -> iter:
    api_response = get_movies_showtimes_from_api(api_key, theater_id)
    movies_showtimes = api_response["movieShowtimeList"]["edges"]
    movies_number = api_response["movieShowtimeList"]["totalCount"]
    filtered_movies_showtimes = _filter_only_non_special_events_type_movie_showtimes(movies_showtimes)

    logger.info('[ALLOCINE] Total : %s movies' % movies_number)

    return iter(filtered_movies_showtimes)


def get_movie_poster(poster_url: str,
                     get_movie_poster_from_api: Callable = get_movie_poster_from_allocine) -> bytes:
    return get_movie_poster_from_api(poster_url)

def _filter_only_non_special_events_type_movie_showtimes(movies_showtime: list) -> list:
    return list(filter(lambda movie_showtime: movie_showtime['node']['movie']['type'] != MOVIE_TYPE, movies_showtime))
