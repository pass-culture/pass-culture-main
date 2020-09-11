import os

import requests
from typing import Dict

FNAC_API_RESULTS_LIMIT = 1000 # todo : quid du cas FNAC ?
FNAC_API_URL = 'https://passculture-fr.ws.fnac.com/api/v1/pass-culture/stocks/'


class ApiFnacException(Exception):
    pass


def get_stocks_from_fnac_api(siret: str, last_processed_isbn: str = '', modified_since: str = '',
                             limit: int = FNAC_API_RESULTS_LIMIT) -> Dict:
    api_url = _build_fnac_url(siret)
    params = _build_fnac_params(last_processed_isbn, modified_since, limit)
    fnac_api_basicauth_token = os.environ.get('PROVIDER_FNAC_BASICAUTH_TOKEN')

    fnac_response = requests.get(api_url,
                                 params=params,
                                 headers={'Authorization': f'Basic {fnac_api_basicauth_token}'})

    if fnac_response.status_code != 200:
        raise ApiFnacException(f'Error {fnac_response.status_code} when getting Fnac stocks for SIRET:'
                               f' {siret}')

    return fnac_response.json()


def is_siret_registered(siret: str) -> bool:
    api_url = _build_fnac_url(siret)
    fnac_response = requests.get(api_url)

    return fnac_response.status_code == 200


def _build_fnac_url(siret: str) -> str:
    return f'{FNAC_API_URL}/{siret}'


def _build_fnac_params(last_processed_isbn: str, modified_since: str, limit: int) -> Dict:
    params = {'limit': str(limit)}
    if last_processed_isbn:
        params['after'] = last_processed_isbn  # todo: même fonctionnement pour la FNAC ?
    if modified_since:
        params['modifiedSince'] = modified_since

    return params
