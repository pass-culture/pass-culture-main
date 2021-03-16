from typing import List

from pcapi.core.offerers.models import Offerer
from pcapi.models import Venue
from pcapi.repository.iris_venues_queries import find_ids_of_irises_located_near_venue
from pcapi.repository.iris_venues_queries import insert_venue_in_iris_venue


def link_irises_to_existing_physical_venues(search_radius: int):
    venue_ids = _find_all_venue_ids_to_link()
    for venue_id in venue_ids:
        iris_ids = find_ids_of_irises_located_near_venue(venue_id, search_radius)
        insert_venue_in_iris_venue(venue_id, iris_ids)


def _find_all_venue_ids_to_link() -> List[int]:
    venues = (
        Venue.query.join(Offerer)
        .filter(Venue.isVirtual.is_(False))
        .filter(Venue.validationToken.is_(None))
        .filter(Offerer.validationToken.is_(None))
        .with_entities(Venue.id)
        .all()
    )
    return [venue.id for venue in venues]
