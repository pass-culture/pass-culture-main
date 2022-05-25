import pytest

from pcapi.core.offerers.factories import OffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.repository import offerer_has_venue_with_adage_id


pytestmark = pytest.mark.usefixtures("db_session")


class OffererHasAdageIdTest:
    def test_ok(self):
        venue = VenueFactory(adageId="123")

        result = offerer_has_venue_with_adage_id(venue.managingOfferer.id)

        assert result

    def test_offerer_with_multiple_venue_with_adage_id(self):
        offerer = OffererFactory()
        VenueFactory(managingOfferer=offerer, adageId="123")
        VenueFactory(managingOfferer=offerer, adageId="124")

        result = offerer_has_venue_with_adage_id(offerer.id)

        assert result is True

    def test_no_venue(self):
        offerer = OffererFactory()

        result = offerer_has_venue_with_adage_id(offerer.id)

        assert result is False

    def test_venue_without_adage_id(self):
        venue = VenueFactory(adageId=None)

        result = offerer_has_venue_with_adage_id(venue.managingOfferer.id)

        assert result is False

    def test_no_offerer(self):
        result = offerer_has_venue_with_adage_id(123654987)

        assert result is False
