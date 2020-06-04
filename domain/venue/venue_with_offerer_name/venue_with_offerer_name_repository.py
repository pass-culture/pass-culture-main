from abc import ABC, abstractmethod
from typing import List

from domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName


class VenueWithOffererNameRepository(ABC):
    @abstractmethod
    def get_by_pro_identifier(self, pro_identifier: int) -> List[VenueWithOffererName]:
        pass
