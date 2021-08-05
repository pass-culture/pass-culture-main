import pytest

from pcapi.core.offerers.factories import VenueTypeFactory
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import VenueFactory
from pcapi.scripts.update_venue_type_codes import update_venues_codes


@pytest.mark.usefixtures("db_session")
def test_update_venue_codes(app):
    bookstore_type = VenueTypeFactory(label="Librairie")
    museum_type = VenueTypeFactory(label="Musée")
    digital_type = VenueTypeFactory(label="Offre numérique")

    bookstore = VenueFactory(venueType=bookstore_type, venueTypeCode=None)
    museum = VenueFactory(venueType=museum_type, venueTypeCode=None)
    digital = VenueFactory(venueType=digital_type, venueTypeCode=None)
    undefined = VenueFactory(venueType=None, venueTypeCode=None)

    update_venues_codes()

    assert Venue.query.get(bookstore.id).venueTypeCode.value == "BOOKSTORE"
    assert Venue.query.get(museum.id).venueTypeCode.value == "MUSEUM"
    assert Venue.query.get(digital.id).venueTypeCode.value == "DIGITAL"
    assert Venue.query.get(undefined.id).venueTypeCode.value == "OTHER"
