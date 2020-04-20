from typing import List

from models import VenueType


def get_all_venue_types() -> List[VenueType]:
    return VenueType.query.all()
