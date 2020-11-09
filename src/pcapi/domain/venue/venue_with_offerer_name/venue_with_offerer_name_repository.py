from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional

from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName


class VenueWithOffererNameRepository(ABC):
    @abstractmethod
    def get_by_pro_identifier(self,
                              pro_identifier: int,
                              user_is_admin: bool,
                              offerer_id: Optional[Identifier] = None,) -> List[VenueWithOffererName]:
        pass
