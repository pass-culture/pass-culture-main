from pcapi.infrastructure.container import api_titelive_stocks
from pcapi.local_providers.generic_provider.generic_stocks import GenericStocks


class TiteLiveStocks(GenericStocks):
    name = "TiteLive Stocks (Epagine / Place des libraires.com)"
    can_create = True
    get_provider_stock_information = api_titelive_stocks.stocks_information
    price_divider_to_euro = 100
