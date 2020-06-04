from typing import List

from domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from domain.venue.venue_with_offerer_name.venue_with_offerer_name_repository import VenueWithOffererNameRepository


class GetVenuesByProUser:
    def __init__(self, venue_repository: VenueWithOffererNameRepository):
        self.venue_repository = venue_repository

    def execute(self, pro_identifier: int) -> List[VenueWithOffererName]:
        return self.venue_repository.get_by_pro_identifier(pro_identifier)
