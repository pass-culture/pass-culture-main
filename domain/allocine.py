from typing import Callable, List

from connectors.api_allocine import get_movie_showtime_list
from utils.logger import logger


def get_movie_showtime_list_from_allocine(token: str, theater_id : str,
                                          get_movie_showtime_list_api: Callable = get_movie_showtime_list
                                          ) -> List[dict]:

    api_response = get_movie_showtime_list_api(token, theater_id)
    movie_showtime_list = api_response["movieShowtimeList"]["edges"]
    movies_number = api_response["movieShowtimeList"]["totalCount"]

    logger.info('[ALLOCINE] Total : %s movies' % movies_number)

    return movie_showtime_list
