from datetime import datetime
from typing import Iterator, Dict

from connectors.api_local_provider import ApiLocalProvider
from domain.stock_provider.stock_provider_repository import StockProviderRepository


class StockProviderLibrairesRepository(StockProviderRepository):
    def __init__(self):
        self.api_local_provider = ApiLocalProvider(api_url='https://passculture.leslibraires.fr/stocks',
                                                   name='Libraires')

    def stocks_information(self, siret: str,
                           last_processed_reference: str = '',
                           modified_since: datetime = None) -> Iterator[Dict]:
        modified_since = datetime.strftime(modified_since, "%Y-%m-%dT%H:%M:%SZ") if modified_since else ''
        return self.api_local_provider.get_stocks_from_local_provider_api(siret=siret,
                                                                          last_processed_isbn=last_processed_reference,
                                                                          modified_since=modified_since)

    def can_be_synchronized(self, siret: str) -> bool:
        return self.api_local_provider.is_siret_registered(siret)
