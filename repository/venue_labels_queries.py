from typing import List

from models.venue_label import VenueLabel


def get_all_venue_labels() -> List[VenueLabel]:
    return VenueLabel.query.all()
