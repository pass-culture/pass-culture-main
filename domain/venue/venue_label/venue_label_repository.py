from abc import ABC, abstractmethod
from typing import List

from domain.venue.venue_label.venue_label import VenueLabel


class VenueLabelRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[VenueLabel]:
        pass
