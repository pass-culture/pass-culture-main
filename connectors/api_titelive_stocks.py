import requests

TITELIVE_STOCKS_API_URL = 'https://stock.epagine.fr/stocks'


class ApiTiteLiveException(Exception):
    pass


def get_titelive_stocks(siret: str, last_processed_isbn: str = '') -> dict:
    url = _build_url(siret, last_processed_isbn)
    api_response = requests.get(url)

    if api_response.status_code != 200:
        raise ApiTiteLiveException(f'Error {api_response.status_code} when getting TiteLive stocks for siret: {siret}')

    return api_response.json()


def _build_url(siret: str, last_processed_isbn: str = '') -> str:
    url = f'{TITELIVE_STOCKS_API_URL}/{siret}'
    if last_processed_isbn:
        return f'{url}?after={last_processed_isbn}'
    return url
