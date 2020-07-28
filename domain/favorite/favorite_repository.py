from abc import ABC, abstractmethod

from models import FavoriteSQLEntity


class FavoriteRepository(ABC):
    @abstractmethod
    def find_by_beneficiary(self, beneficiary_identifier: int) -> FavoriteSQLEntity:
        pass
