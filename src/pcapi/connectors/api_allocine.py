import requests

from utils.logger import json_logger

API_ALLOCINE = "ApiAllocine"


class AllocineException(Exception):
    pass


def get_movies_showtimes_from_allocine(api_key: str, theater_id: str) -> dict:
    api_url = f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?token={api_key}&theater={theater_id}"

    try:
        api_response = requests.get(api_url)
        json_logger.info("Loading movie showtimes from Allocine",
                         extra={'theater': theater_id, "service": API_ALLOCINE})
    except Exception:
        json_logger.error("Error connecting to Allocine API", extra={'theater': theater_id, "service": API_ALLOCINE})
        raise AllocineException(f'Error connecting Allocine API for theater {theater_id}')

    if api_response.status_code != 200:
        json_logger.error("Error in request to Allocine API", extra={'theater': theater_id, "service": API_ALLOCINE})
        raise AllocineException(f'Error getting API Allocine DATA for theater {theater_id}')

    return api_response.json()


def get_movie_poster_from_allocine(poster_url: str) -> bytes:
    api_response = requests.get(poster_url)
    json_logger.info("Loading movie poster from Allocine",
                     extra={"poster": poster_url, "service": API_ALLOCINE})

    if api_response.status_code != 200:
        json_logger.error("Failed to load movie poster from Allocine",
                          extra={"poster": poster_url, "service": API_ALLOCINE})
        raise AllocineException(f'Error getting API Allocine movie poster {poster_url}'
                                f' with code {api_response.status_code}')

    return api_response.content
