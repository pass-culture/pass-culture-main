from domain.venue.venue_repository import VenueRepository


class GetAllVenuesByProUser:
    def __init__(self, venue_repository: VenueRepository):
        self.venue_repository = venue_repository

    def execute(self, pro_identifier: int):
        return self.venue_repository.get_all_by_pro_identifier(pro_identifier)
