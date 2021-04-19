from pcapi.models import VenueType


def get_all_venue_types() -> list[VenueType]:
    return VenueType.query.all()
