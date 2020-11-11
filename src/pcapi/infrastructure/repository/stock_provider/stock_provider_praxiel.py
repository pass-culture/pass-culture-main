from datetime import datetime
from typing import Dict
from typing import Iterator

from pcapi.domain.stock_provider.stock_provider_repository import StockProviderRepository
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI


class StockProviderPraxielRepository(StockProviderRepository):
    def __init__(self) -> None:
        self.praxiel_api = ProviderAPI(api_url="https://www.praxiel-passculture.fr/stocks", name="Praxiel/Inference")

    def stocks_information(
        self, siret: str, last_processed_reference: str = "", modified_since: datetime = None
    ) -> Iterator[Dict]:
        modified_since = datetime.strftime(modified_since, "%Y-%m-%dT%H:%M:%SZ") if modified_since else ""
        stocks = self.praxiel_api.stocks(
            siret=siret, last_processed_reference=last_processed_reference, modified_since=modified_since
        )
        return iter(stocks.get("stocks", []))

    def can_be_synchronized(self, siret: str) -> bool:
        return self.praxiel_api.is_siret_registered(siret=siret)
