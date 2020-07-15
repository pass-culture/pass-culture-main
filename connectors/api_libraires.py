from typing import Dict

import requests

LIBRAIRES_API_RESULTS_LIMIT = 1000
LIBRAIRES_API_URL = 'https://passculture.leslibraires.fr/stocks'


class ApiLibrairesException(Exception):
    pass


def get_stocks_from_libraires_api(siret: str, last_processed_isbn: str = '', modified_since: str = '', limit: int = LIBRAIRES_API_RESULTS_LIMIT) -> Dict:
    api_url = _build_libraires_url(siret)
    params = _build_libraires_params(last_processed_isbn, modified_since, limit)

    libraires_response = requests.get(api_url, params=params)

    if libraires_response.status_code != 200:
        raise ApiLibrairesException(f'Error {libraires_response.status_code} when getting Libraires stocks for SIRET:'
                                    f' {siret}')

    return libraires_response.json()


def is_siret_registered(siret: str) -> bool:
    api_url = _build_libraires_url(siret)
    libraires_response = requests.get(api_url)

    return libraires_response.status_code == 200


def _build_libraires_url(siret: str) -> str:
    return f'{LIBRAIRES_API_URL}/{siret}'


def _build_libraires_params(last_processed_isbn: str, modified_since: str, limit: int) -> Dict:
    params = {'limit': str(limit)}
    if last_processed_isbn:
        params['after'] = last_processed_isbn
    if modified_since:
        params['modifiedSince'] = modified_since

    return params
