from pcapi.infrastructure.container import api_praxiel_stocks
from pcapi.local_providers.generic_provider.generic_stocks import GenericStocks


class PraxielStocks(GenericStocks):
    name = "Praxiel/Inférence"
    can_create = True
    get_provider_stock_information = api_praxiel_stocks.stocks_information
