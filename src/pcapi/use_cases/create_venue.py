from typing import Callable

from pcapi.domain.iris import link_valid_venue_to_irises
from pcapi.models import Venue


def create_venue(venue_properties: dict, save: Callable) -> Venue:
    venue = Venue(from_dict=venue_properties)

    save(venue)

    link_valid_venue_to_irises(venue=venue)

    return venue
