from abc import ABC, abstractmethod
from typing import List

from domain.venue.venue_with_offerer_informations.venue_with_offerer_informations import VenueWithOffererInformations


class VenueWithOffererInformationsRepository(ABC):
    @abstractmethod
    def get_by_pro_identifier(self, pro_identifier: int) -> List[VenueWithOffererInformations]:
        pass
