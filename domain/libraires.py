from typing import Callable

from connectors.api_libraires import ApiHttpLibrairesStocks

LIBRAIRES_STOCK_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def get_libraires_stock_information(siret: str, last_processed_isbn: str = '', modified_since: str = '',
                                    get_libraires_stocks: Callable = None) -> iter:
    api_response = get_libraires_stocks(siret, last_processed_isbn, modified_since)
    return iter(api_response['stocks'])


def can_be_synchronized_with_libraires(siret: str) -> bool:
    api = ApiHttpLibrairesStocks(api_url=API_URL, name='Libraires')
    return api.is_siret_registered(siret)
