from abc import ABC
from abc import abstractmethod

from pcapi.domain.venue.venue_label.venue_label import VenueLabel


class VenueLabelRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[VenueLabel]:
        pass
