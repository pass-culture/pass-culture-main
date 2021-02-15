from pcapi.core.offerers.models import Venue
from pcapi.models import VenueType


def create_digital_venue(offerer):
    digital_venue = Venue()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeId = _get_digital_venue_type_id()
    digital_venue.managingOfferer = offerer
    return digital_venue


def _get_digital_venue_type_id() -> int:
    return VenueType.query.filter_by(label="Offre numérique").first().id
