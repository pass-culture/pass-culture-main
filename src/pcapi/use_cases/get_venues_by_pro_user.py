from typing import List
from typing import Optional

from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name_repository import VenueWithOffererNameRepository


class GetVenuesByProUser:
    def __init__(self, venue_repository: VenueWithOffererNameRepository):
        self.venue_repository = venue_repository

    def execute(self,
                pro_identifier: int,
                user_is_admin: bool,
                offerer_id: Optional[Identifier] = None,) -> List[VenueWithOffererName]:
        return self.venue_repository.get_by_pro_identifier(pro_identifier, user_is_admin, offerer_id)
