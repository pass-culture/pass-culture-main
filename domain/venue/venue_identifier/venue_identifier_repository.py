from abc import ABC, abstractmethod
from typing import List

from domain.venue.venue_identifier.venue_identifier import VenueIdentifier


class VenueIdentifierRepository(ABC):
    @abstractmethod
    def find_by_siret(self, siret: str) -> VenueIdentifier:
        pass

    @abstractmethod
    def find_by_name(self, name: str, offerer_id: int) -> List[VenueIdentifier]:
        pass
