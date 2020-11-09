from typing import Callable

from pcapi.models import VenueSQLEntity
from pcapi.repository.iris_venues_queries import find_ids_of_irises_located_near_venue
from pcapi.repository.iris_venues_queries import insert_venue_in_iris_venue


MAXIMUM_DISTANCE_IN_METERS = 100000


def _link_venue_to_irises(venue: VenueSQLEntity) -> None:
    if not venue.isVirtual:
        iris_ids_near_venue = find_ids_of_irises_located_near_venue(venue.id, MAXIMUM_DISTANCE_IN_METERS)
        insert_venue_in_iris_venue(venue.id, iris_ids_near_venue)


def link_valid_venue_to_irises(venue: VenueSQLEntity, link_venue_to_irises: Callable = _link_venue_to_irises) -> None:
    if venue.isValidated and venue.managingOfferer.isValidated:
        link_venue_to_irises(venue)
