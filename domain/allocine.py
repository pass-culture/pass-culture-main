from typing import Callable, List

from connectors.api_allocine import get_movies_showtimes_from_allocine, get_movie_poster_from_allocine
from local_providers.provider_manager import get_local_provider_class_by_name
from models import Offer
from utils.logger import logger

MOVIE_SPECIAL_EVENT = 'SPECIAL_EVENT'


def get_movies_showtimes(api_key: str, theater_id: str,
                         get_movies_showtimes_from_api: Callable = get_movies_showtimes_from_allocine
                         ) -> iter:
    api_response = get_movies_showtimes_from_api(api_key, theater_id)
    movies_showtimes = api_response["movieShowtimeList"]["edges"]
    movies_number = api_response["movieShowtimeList"]["totalCount"]
    filtered_movies_showtimes = _exclude_movie_showtimes_with_special_event_type(movies_showtimes)

    logger.info('[ALLOCINE] Total : %s movies' % movies_number)

    return iter(filtered_movies_showtimes)


def get_movie_poster(poster_url: str,
                     get_movie_poster_from_api: Callable = get_movie_poster_from_allocine) -> bytes:
    return get_movie_poster_from_api(poster_url)


def _exclude_movie_showtimes_with_special_event_type(movies_showtime: list) -> list:
    return list(filter(lambda movie_showtime: movie_showtime['node']['movie']['type'] != MOVIE_SPECIAL_EVENT, movies_showtime))


def get_editable_fields_for_allocine_offer(offer: Offer, allocine_class_name: str) -> List:
    local_class = offer.lastProvider.localClass
    provider_class = get_local_provider_class_by_name(local_class)
    if local_class == allocine_class_name:
        return provider_class.manually_editable_fields
    return []
