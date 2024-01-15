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
        try:
            response = api_allocine.get_movie_list_page(end_cursor)
        except api_allocine.AllocineException as exc:
            logger.exception("Could not get movies page at cursor '%s'. Error: '%s'", end_cursor, exc)
            break

        movie_list += response.movieList.movies
        end_cursor = response.movieList.pageInfo.endCursor
        has_next_page = response.movieList.pageInfo.hasNextPage

    return movie_list


def get_movies_showtimes(theater_id: str) -> Iterator[allocine_serializers.AllocineMovieShowtime]:
    try:
        movie_showtime_list_response = api_allocine.get_movies_showtimes_from_allocine(theater_id)
    except api_allocine.AllocineException as exc:
        logger.error("Could not get movies showtimes for theater %s. Error: '%s'", theater_id, str(exc))
        return iter([])

    movie_showtime_list = movie_showtime_list_response.movieShowtimeList
    movies_number = movie_showtime_list.totalCount
    filtered_movies_showtimes = _exclude_empty_movies_and_special_events(movie_showtime_list.moviesShowtimes)

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


def _exclude_empty_movies_and_special_events(
    movies_showtimes: list[allocine_serializers.AllocineMovieShowtime],
) -> list[allocine_serializers.AllocineMovieShowtime]:
    return [
        movie_showtimes
        for movie_showtimes in movies_showtimes
        if movie_showtimes.movie and movie_showtimes.movie.type != MOVIE_SPECIAL_EVENT
    ]
