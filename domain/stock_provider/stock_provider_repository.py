import datetime
from abc import ABC, abstractmethod
from typing import Iterator, Dict


class StockProviderRepository(ABC):
    @abstractmethod
    def stocks_information(self, siret: str,
                           last_processed_reference: str = '',
                           modified_since: datetime = None) -> Iterator[Dict]:
        pass

    @abstractmethod
    def can_be_synchronized(self, siret: str) -> bool:
        pass
