import os
from typing import Dict

import requests
from simplejson import JSONDecodeError

FNAC_API_URL = 'https://passculture-fr.ws.fnac.com/api/v1/pass-culture/stocks'


class ApiFnacException(Exception):
    pass


def get_stocks_from_fnac_api(siret: str, last_processed_isbn: str = '', modified_since: str = '',
                             limit: int = 1000) -> Dict:
    api_url = _build_fnac_url(siret)
    params = _build_fnac_params(last_processed_isbn, modified_since, limit)
    basic_authentication_token = os.environ.get('PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN')

    fnac_response = requests.get(api_url,
                                 params=params,
                                 headers={'Authorization': f'Basic {basic_authentication_token}'})

    if fnac_response.status_code != 200:
        raise ApiFnacException(f'Error {fnac_response.status_code} when getting Fnac stocks for SIRET: {siret}')

    try:
        return fnac_response.json()
    except JSONDecodeError:
        return {}


def is_siret_registered(siret: str) -> bool:
    api_url = _build_fnac_url(siret)
    basic_authentication_token = os.environ.get('PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN')
    fnac_response = requests.get(api_url, headers={'Authorization': f'Basic {basic_authentication_token}'})

    return fnac_response.status_code == 200


def _build_fnac_url(siret: str) -> str:
    return f'{FNAC_API_URL}/{siret}'


def _build_fnac_params(last_processed_isbn: str, modified_since: str, limit: int) -> Dict:
    params = {'limit': str(limit)}
    if last_processed_isbn:
        params['after'] = last_processed_isbn
    if modified_since:
        params['modifiedSince'] = modified_since

    return params
