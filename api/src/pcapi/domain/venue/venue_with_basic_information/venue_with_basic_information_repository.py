from abc import ABC
from abc import abstractmethod

from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation


class VenueWithBasicInformationRepository(ABC):
    @abstractmethod
    def find_by_siret(self, siret: str) -> VenueWithBasicInformation | None:
        pass

    @abstractmethod
    def find_by_name(self, name: str, offerer_id: int) -> list[VenueWithBasicInformation]:
        pass
