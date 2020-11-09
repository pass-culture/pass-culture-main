from abc import ABC
from abc import abstractmethod

from pcapi.domain.stock.stock import Stock


class StockRepository(ABC):
    @abstractmethod
    def find_stock_by_id(self, stock_id: int) -> Stock:
        pass
