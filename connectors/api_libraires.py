from typing import Dict

import requests


class ApiLibrairesException(Exception):
    pass


def get_stocks_from_libraires_api(siret: str, last_processed_isbn: str = '', modified_since: str = '') -> Dict:
    api_url = _build_libraires_url(siret, last_processed_isbn, modified_since)
    libraires_response = requests.get(api_url)

    if libraires_response.status_code != 200:
        raise ApiLibrairesException(f'Error {libraires_response.status_code} when getting Libraires stocks for SIRET:'
                                    f' {siret}')

    return libraires_response.json()


def _build_libraires_url(siret: str, last_processed_isbn: str = '', modified_since: str = '') -> str:
    libraires_api_url = 'https://passculture.leslibraires.fr/stocks'
    libraires_api_results_limit = 1000

    api_url = f'{libraires_api_url}/{siret}?limit={libraires_api_results_limit}'
    if last_processed_isbn:
        api_url = f'{api_url}&after={last_processed_isbn}'
    if modified_since:
        api_url = f'{api_url}&modifiedSince={modified_since}'
    return api_url
