from typing import List

from domain.venue.venue_with_offerer_informations.venue_with_offerer_informations import VenueWithOffererInformations
from domain.venue.venue_with_offerer_informations.venue_with_offerer_informations_repository import VenueWithOffererInformationsRepository


class GetVenuesByProUser:
    def __init__(self, venue_repository: VenueWithOffererInformationsRepository):
        self.venue_repository = venue_repository

    def execute(self, pro_identifier: int) -> List[VenueWithOffererInformations]:
        return self.venue_repository.get_by_pro_identifier(pro_identifier)
