import requests
from typing import Dict

TITELIVE_STOCKS_API_URL = 'https://stock.epagine.fr/stocks'


class ApiTiteLiveException(Exception):
    pass


def get_titelive_stocks(siret: str, last_processed_isbn: str = '', modified_since: str = None) -> Dict:
    url = _build_url(siret)
    params = _build_params(last_processed_isbn, modified_since)

    api_response = requests.get(url, params=params)

    if api_response.status_code != 200:
        raise ApiTiteLiveException(f'Error {api_response.status_code} when getting TiteLive stocks for siret: {siret}')

    return api_response.json()


def is_siret_registered(siret: str) -> bool:
    api_url = _build_url(siret)
    libraires_response = requests.get(api_url)

    return libraires_response.status_code == 200


def _build_url(siret: str) -> str:
    return f'{TITELIVE_STOCKS_API_URL}/{siret}'


def _build_params(last_processed_isbn: str = '', modified_since: str = None) -> Dict:
    params = {}
    if last_processed_isbn:
        params['after'] = last_processed_isbn
    if modified_since:
        params['modifiedSince'] = modified_since

    return params
