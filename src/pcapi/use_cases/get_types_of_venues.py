from typing import Callable

from pcapi.models import VenueType


def get_types_of_venues(get_all_venue_types: Callable) -> list[VenueType]:
    return get_all_venue_types()
