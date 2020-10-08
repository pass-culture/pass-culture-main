import os
from datetime import datetime
from typing import Dict, Iterator

from pcapi.domain.stock_provider.stock_provider_repository import StockProviderRepository
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI


class StockProviderFnacRepository(StockProviderRepository):
    def __init__(self) -> None:
        self.fnac_api = ProviderAPI(api_url='https://passculture-fr.ws.fnac.com/api/v1/pass-culture/stocks',
                                    name='Fnac',
                                    authentication_token=os.environ.get('PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN'))

    def stocks_information(self, siret: str,
                           last_processed_reference: str = '',
                           modified_since: datetime = None) -> Iterator[Dict]:
        modified_since = datetime.strftime(modified_since, "%Y-%m-%dT%H:%M:%SZ") if modified_since else ''
        stocks = self.fnac_api.stocks(siret=siret,
                                      last_processed_reference=last_processed_reference,
                                      modified_since=modified_since)
        return iter(stocks.get('stocks', []))

    def can_be_synchronized(self, siret: str) -> bool:
        return self.fnac_api.is_siret_registered(siret=siret)
