from models import Venue, Offerer
from repository.iris_venues_queries import find_ids_of_irises_located_near_venue, insert_venue_in_iris_venue


def link_irises_to_existing_physical_venues():
    venues = _find_all_venues_to_link()
    for venue in venues:
        iris_ids = find_ids_of_irises_located_near_venue(venue.id)
        insert_venue_in_iris_venue(venue.id, iris_ids)


def _find_all_venues_to_link():
    return Venue.query\
        .join(Offerer) \
        .filter(Venue.isVirtual == False) \
        .filter(Venue.validationToken == None) \
        .filter(Offerer.validationToken == None) \
        .all()
