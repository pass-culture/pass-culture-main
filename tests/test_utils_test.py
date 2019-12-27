from models import Offerer, PcObject, Venue
from tests.conftest import clean_database

from tests.test_utils import create_venue

class CreateVenueTest:
    @clean_database
    def test_create_virtual_venue_should_not_have_latitude_and_longitude(self, app):
        # Given
        offerer = Offerer()

        # When
        venue = create_venue(
            offerer,
            is_virtual=True,
            siret=None,
            name='Virtual Venue'
        )

        # Then
        assert venue.address == None
        assert venue.latitude == None
        assert venue.longitude == None
