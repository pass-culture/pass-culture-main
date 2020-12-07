from pcapi.infrastructure.container import api_libraires_stocks
from pcapi.local_providers.generic_provider.generic_stocks import GenericStocks


class LibrairesStocks(GenericStocks):
    name = "Leslibraires.fr"
    can_create = True
    get_provider_stock_information = api_libraires_stocks.stocks_information
