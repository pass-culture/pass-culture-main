from models import Venue
from repository.iris_venues_queries import find_iris_near_venue, insert_venue_in_iris_venues


def add_venue_to_iris_venues(venue: Venue) -> None:
    if not venue.isVirtual and venue.isValidated:
        iris_ids_near_venue = find_iris_near_venue(venue.id)
        insert_venue_in_iris_venues(venue.id, iris_ids_near_venue)
