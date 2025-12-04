import pytest

from pcapi.core.offerers import factories
from pcapi.core.offerers import models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class VenueFactoryTest:
    def test_venue_offerer_address(self):
        venue = factories.VenueFactory()

        assert venue.offererAddress is not None
        assert venue.offererAddress.type == models.LocationType.VENUE_LOCATION
        assert venue.offererAddress.venue == venue
        assert venue.offererAddress.offerer == venue.managingOfferer

        assert db.session.query(models.Venue).count() == 1
        assert db.session.query(models.OffererAddress).count() == 1


class OffererAddressFactoryTest:
    def test_legacy_offerer_address_factory(self):
        offerer_address = factories.OffererAddressFactory()
        assert offerer_address.type is None
        assert offerer_address.venue is None

    def test_venue_location_factory(self):
        venue_location = factories.VenueLocationFactory()
        assert venue_location.type == models.LocationType.VENUE_LOCATION
        assert venue_location.venue.managingOfferer == venue_location.offerer
        assert venue_location.venue.offererAddress == venue_location

    def test_offer_location_factory(self):
        offer_location = factories.OfferLocationFactory()
        assert offer_location.type == models.LocationType.OFFER_LOCATION
        assert offer_location.venue.managingOfferer == offer_location.offerer
