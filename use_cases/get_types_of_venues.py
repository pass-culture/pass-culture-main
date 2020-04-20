from typing import Callable, List

from models import VenueType


def get_types_of_venues(get_all_venue_types: Callable) -> List[VenueType]:
    return get_all_venue_types()
