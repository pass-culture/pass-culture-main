import pytest

from pcapi.core.offerers import factories
from pcapi.core.offerers.addresses.api import get_venue_offerer_addresses
from pcapi.core.offerers.addresses.api import get_venue_other_offerer_addresses_ids
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="offerer")
def offerer_fixture():
    return factories.OffererFactory()


@pytest.fixture(name="offerer_address")
def offerer_addres_fixture(offerer):
    return factories.OffererAddressFactory(offerer=offerer)


class GetVenueOtherOffererAddressesIdsTest:
    def test_venue_has_no_other_address_and_nothing_is_returned(self, offerer, offerer_address):
        venue = factories.VenueFactory(offererAddress=offerer_address, managingOfferer=offerer)
        stmt = get_venue_other_offerer_addresses_ids(venue)
        assert not db.session.execute(stmt).all()

    def test_virtual_venue_has_no_other_address_and_nothing_is_returned(self, offerer, offerer_address):
        venue = factories.VirtualVenueFactory(managingOfferer=offerer)
        stmt = get_venue_other_offerer_addresses_ids(venue)
        assert not db.session.execute(stmt).all()

    def test_venue_has_many_other_addresses_and_all_are_returned(self, offerer, offerer_address):
        venue = factories.VenueFactory(offererAddress=offerer_address, managingOfferer=offerer)

        offers = [
            offers_factories.OfferFactory(venue=venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)),
            offers_factories.OfferFactory(venue=venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)),
            offers_factories.OfferFactory(venue=venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)),
        ]

        stmt = get_venue_other_offerer_addresses_ids(venue)
        res = db.session.execute(stmt).all()

        assert len(res) == len(offers)
        assert {o.offererAddressId for o in offers} == {row[0] for row in res}


class GetVenueOffererAddressesTest:
    """
    Check that `get_venue_offerer_addresses` always return a venue's
    offerer addresses which means: its own (unless it is a virtual venue
    and it has none) and other addresses from its offers (if any).
    """

    def test_venue_has_no_other_address_and_only_one_address_is_returned(self, offerer, offerer_address):
        venue = factories.VenueFactory(offererAddress=offerer_address, managingOfferer=offerer)
        res = list(get_venue_offerer_addresses(venue))

        assert len(res) == 1
        assert res[0].id == venue.offererAddressId

    def test_venue_has_many_other_addresses_and_all_are_returned(self, offerer, offerer_address):
        venue = factories.VenueFactory(offererAddress=offerer_address, managingOfferer=offerer)

        offers = [
            offers_factories.OfferFactory(venue=venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)),
            offers_factories.OfferFactory(venue=venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)),
            offers_factories.OfferFactory(venue=venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)),
        ]

        res = list(get_venue_offerer_addresses(venue))
        assert len(res) == len(offers) + 1
        assert ({o.offererAddressId for o in offers} | {venue.offererAddressId}) == {oa.id for oa in res}

    def test_address_from_other_venues_from_same_offerer_are_ignored(self, offerer, offerer_address):
        venue = factories.VenueFactory(offererAddress=offerer_address, managingOfferer=offerer)
        offer = offers_factories.OfferFactory(
            venue=venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)
        )

        another_oa = factories.OffererAddressFactory(offerer=offerer)
        other_venue = factories.VenueFactory(offererAddress=another_oa, managingOfferer=offerer)
        offers_factories.OfferFactory(
            venue=other_venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)
        )

        res = list(get_venue_offerer_addresses(venue))
        assert len(res) == 2
        assert {venue.offererAddressId, offer.offererAddressId} == {oa.id for oa in res}

    def test_address_from_other_venues_from_other_offerer_are_ignored(self, offerer, offerer_address):
        venue = factories.VenueFactory(offererAddress=offerer_address, managingOfferer=offerer)
        offer = offers_factories.OfferFactory(
            venue=venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)
        )

        another_offerer = factories.OffererFactory()
        another_oa = factories.OffererAddressFactory(offerer=another_offerer)
        other_venue = factories.VenueFactory(offererAddress=another_oa, managingOfferer=offerer)
        offers_factories.OfferFactory(
            venue=other_venue, offererAddress=factories.OffererAddressFactory(offerer=offerer)
        )

        res = list(get_venue_offerer_addresses(venue))
        assert len(res) == 2
        assert {venue.offererAddressId, offer.offererAddressId} == {oa.id for oa in res}
