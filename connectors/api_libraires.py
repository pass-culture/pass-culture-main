import requests

LIBRAIRES_API_URL = 'https://passculture.leslibraires.fr/stocks'
LIBRAIRES_RESPONSE_DATA_LIMIT = 1000


class ApiLibrairesException(Exception):
    pass


def get_stocks_from_libraires_api(siret: str, last_processed_isbn: str = '', modified_since: str = '') -> dict:
    api_url = _build_libraires_url(siret, last_processed_isbn, modified_since)
    libraires_response = requests.get(api_url)

    if libraires_response.status_code != 200:
        raise ApiLibrairesException(f'Error getting Libraires stocks for siret: {siret}')

    return libraires_response.json()


def _build_libraires_url(siret: str, last_processed_isbn: str = '', modified_since: str = '') -> str:
    api_url = f'{LIBRAIRES_API_URL}/{siret}?limit={LIBRAIRES_RESPONSE_DATA_LIMIT}'
    if modified_since and last_processed_isbn:
        return f'{api_url}&after={last_processed_isbn}&modifiedSince={modified_since}'
    if modified_since:
        return f'{api_url}&modifiedSince={modified_since}'
    if last_processed_isbn:
        return f'{api_url}&after={last_processed_isbn}'
    return api_url
