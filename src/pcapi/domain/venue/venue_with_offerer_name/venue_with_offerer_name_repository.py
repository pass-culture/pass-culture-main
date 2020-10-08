from abc import ABC, abstractmethod
from typing import List

from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName


class VenueWithOffererNameRepository(ABC):
    @abstractmethod
    def get_by_pro_identifier(self, pro_identifier: int, user_is_admin: bool) -> List[VenueWithOffererName]:
        pass
