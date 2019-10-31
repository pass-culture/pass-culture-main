import requests


class AllocineException(Exception):
    pass


def get_movies_showtimes_list(token: str, theater_id: str) -> dict:
    allocine_api_url = f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?token={token}&theater={theater_id}"
    api_response = requests.get(allocine_api_url)

    if api_response.status_code != 200:
        raise AllocineException(f'Error getting API Allocine DATA for theater {theater_id}')

    return api_response.json()
