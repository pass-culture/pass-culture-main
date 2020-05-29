from abc import ABC, abstractmethod
from typing import List

from domain.venue.venue import Venue


class VenueRepository(ABC):
    @abstractmethod
    def find_by_siret(self, siret: str) -> Venue:
        pass

    @abstractmethod
    def find_by_name(self, name: str, offerer_id: str) -> List[Venue]:
        pass

    @abstractmethod
    def get_all_by_pro_identifier(self, pro_identifier: int) -> List[Venue]:
        pass
