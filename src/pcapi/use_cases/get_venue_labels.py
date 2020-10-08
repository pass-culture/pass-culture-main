from typing import List

from pcapi.domain.venue.venue_label.venue_label import VenueLabel
from pcapi.domain.venue.venue_label.venue_label_repository import VenueLabelRepository


class GetVenueLabels:
    def __init__(self, venue_label_repository: VenueLabelRepository):
        self.venue_label_repository = venue_label_repository

    def execute(self) -> List[VenueLabel]:
        return self.venue_label_repository.get_all()
