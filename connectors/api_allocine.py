import requests


class AllocineException(Exception):
    pass


def get_movie_showtime_list(token: str, theater_id: str) -> dict:
    api_response = requests.get(
        f"https://graph-api-proxy.allocine.fr/api/query/movieShowtimeList?token={token}&theater={theater_id}")

    if api_response.status_code != 200:
        raise AllocineException(f'Error getting API Allocine DATA for theater {theater_id}')

    return api_response.json()
