from typing import List

from pcapi.models import VenueType


def get_all_venue_types() -> List[VenueType]:
    return VenueType.query.all()
