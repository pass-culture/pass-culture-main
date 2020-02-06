import requests


class AllocineException(Exception):
    pass


def get_movies_showtimes_from_allocine(api_key: str, theater_id: str) -> dict:
    api_url = f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?token={api_key}&theater={theater_id}"

    try:
        api_response = requests.get(api_url)
    except Exception:
        raise AllocineException(f'Error connecting Allocine API for theater {theater_id}')

    if api_response.status_code != 200:
        raise AllocineException(f'Error getting API Allocine DATA for theater {theater_id}')

    return api_response.json()


def get_movie_poster_from_allocine(poster_url: str) -> bytes:
    api_response = requests.get(poster_url)

    if api_response.status_code != 200:
        raise AllocineException(f'Error getting API Allocine movie poster {poster_url}'
                                f' with code {api_response.status_code}')

    return api_response.content
