from abc import ABC
from abc import abstractmethod
from typing import List

from pcapi.domain.favorite.favorite import Favorite


class FavoriteRepository(ABC):
    @abstractmethod
    def find_by_beneficiary(self, beneficiary_identifier: int) -> List[Favorite]:
        pass
