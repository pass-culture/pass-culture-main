
class VenueMatchingError(Exception):
    pass


def check_offerer_presence(offerer):
    if not offerer:
        raise VenueMatchingError("Offerer not found")


def check_venue_presence(venue):
    if not venue:
        raise VenueMatchingError("Venue not found")


def check_venue_queried_by_name(venues):
    if len(venues) == 0:
        raise VenueMatchingError("Venue name for found")
    if len(venues) > 1:
        raise VenueMatchingError("Multiple venues found")
