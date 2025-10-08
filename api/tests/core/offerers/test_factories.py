import pytest

from pcapi.core.offerers import factories
from pcapi.core.offerers import models


pytestmark = pytest.mark.usefixtures("db_session")


class OffererAddressFactoryTest:
    def test_legacy_offerer_address_factory(self):
        offerer_address = factories.OffererAddressFactory()
        assert offerer_address.type is None
        assert offerer_address.venue is None

    def test_venue_location_factory(self):
        venue_location = factories.VenueLocationFactory()
        assert venue_location.type == models.LocationType.VENUE_LOCATION
        assert venue_location.venue.managingOfferer == venue_location.offerer

    def test_offer_location_factory(self):
        offer_location = factories.OfferLocationFactory()
        assert offer_location.type == models.LocationType.OFFER_LOCATION
        assert offer_location.venue.managingOfferer == offer_location.offerer

    def test_unconsistent_location_factory(self):
        with pytest.raises(ValueError):
            factories.VenueLocationFactory(
                offerer=factories.OffererFactory(),
                venue=factories.VenueFactory(),
            )
