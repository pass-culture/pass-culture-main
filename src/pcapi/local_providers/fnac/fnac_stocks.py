from pcapi.infrastructure.container import api_fnac_stocks
from pcapi.local_providers.generic_provider.generic_stocks import GenericStocks


class FnacStocks(GenericStocks):
    name = "FNAC"
    can_create = True
    get_provider_stock_information = api_fnac_stocks.stocks_information
