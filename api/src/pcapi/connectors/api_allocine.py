from pcapi import settings
from pcapi.connectors.serialization import allocine_serializers
from pcapi.utils import requests


class AllocineException(Exception):
    pass


ALLOCINE_API_URL = "https://graph-api-proxy.allocine.fr/api/query"


def get_movie_list_page(after: str = "") -> allocine_serializers.AllocineMovieListResponse:
    url = f"{ALLOCINE_API_URL}/movieList?after={after}"
    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + settings.ALLOCINE_API_KEY})
    except Exception:
        raise AllocineException("Error connecting Allocine API to get movie list")

    if not response.ok:
        raise AllocineException(f"Error getting API Allocine data to get movie list, error={response.status_code}")

    return allocine_serializers.AllocineMovieListResponse.model_validate(response.json())


def get_movies_showtimes_from_allocine(theater_id: str) -> allocine_serializers.AllocineMovieShowtimeListResponse:
    url = f"{ALLOCINE_API_URL}/movieShowtimeList?theater={theater_id}"

    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + settings.ALLOCINE_API_KEY})
    except Exception:
        raise AllocineException(f"Error connecting Allocine API for theater {theater_id}")

    if response.status_code != 200:
        raise AllocineException(f"Error getting API Allocine DATA for theater {theater_id}")

    return allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(response.json())


def get_movie_poster_from_allocine(poster_url: str) -> bytes:
    response = requests.get(poster_url)

    if response.status_code != 200:
        raise AllocineException(
            f"Error getting API Allocine movie poster {poster_url} with code {response.status_code}"
        )

    return response.content
