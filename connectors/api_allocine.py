import requests


class AllocineException(Exception):
    pass


def get_movies_showtimes_from_allocine(api_key: str, theater_id: str) -> dict:
    api_url = f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?token={api_key}&theater={theater_id}"
    api_response = requests.get(api_url)

    if api_response.status_code != 200:
        raise AllocineException(f'Error getting API Allocine DATA for theater {theater_id}')

    return api_response.json()
