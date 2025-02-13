import contextlib
from unittest.mock import patch

import pytest

from pcapi.connectors import api_adresse
from pcapi.connectors.entreprise.backends.testing import TestingBackend
import pcapi.core.geography.factories as geography_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.scripts.transform_virtual_venues.main import FetchAddressError
from pcapi.scripts.transform_virtual_venues.main import MissingSirenError
from pcapi.scripts.transform_virtual_venues.main import NotAVirtualVenue
from pcapi.scripts.transform_virtual_venues.main import get_backend
from pcapi.scripts.transform_virtual_venues.main import get_or_create_offerer_address
from pcapi.scripts.transform_virtual_venues.main import transform_venues_from_offerers_with_one_unique_virtual_venue
from pcapi.scripts.transform_virtual_venues.main import transform_virtual_venue
from pcapi.scripts.transform_virtual_venues.main import venues_from_offerers_with_one_unique_virtual_venue


pytestmark = pytest.mark.usefixtures("db_session")


class VenuesFromOfferersWithOneUniqueVirtualVenueTest:
    def test_one_existing_unique_virtual_offerer(self):
        expected_venue = offerers_factories.VirtualVenueFactory()

        venues = venues_from_offerers_with_one_unique_virtual_venue().all()
        assert len(venues) == 1
        assert venues[0].id == expected_venue.id

    def test_returns_nothing_if_multiple_virtual_venues(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory.create_batch(2, managingOfferer=offerer)

        venues = venues_from_offerers_with_one_unique_virtual_venue().all()
        assert not venues

    def test_returns_venues_from_multiple_matching_offerers(self):
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()

        # venues from offerers that have one (not more) virtual venue
        expected_venues = [
            offerers_factories.VirtualVenueFactory(managingOfferer=offerer1),
            offerers_factories.VirtualVenueFactory(managingOfferer=offerer2),
        ]

        # more than one virtual venue: should not match
        offerer3 = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory.create_batch(2, managingOfferer=offerer3)

        # no virtual venue: should not match
        offerer4 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer4)

        # one virtual and at least one physical venue: should not match
        offerer4 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer4)

        venues = venues_from_offerers_with_one_unique_virtual_venue().all()
        assert len(venues) == len(expected_venues)
        assert {v.id for v in venues} == {v.id for v in expected_venues}


@contextlib.contextmanager
def assert_no_difference(model):
    before_count = model.query.count()
    yield
    assert model.query.count() == before_count


@contextlib.contextmanager
def assert_difference(model, delta=1):
    before_count = model.query.count()
    yield
    assert model.query.count() == before_count + delta


class GetOrCreateOffererAddressTest:
    def test_create_offerer_address(self):
        venue = offerers_factories.VirtualVenueFactory()
        address = geography_factories.AddressFactory()

        with assert_difference(OffererAddress):
            oa = get_or_create_offerer_address(venue.managingOffererId, address.id)
            db.session.commit()

        assert oa.offerer == venue.managingOfferer
        assert oa.address == address

    def test_get_offerer_address(self):
        venue = offerers_factories.VirtualVenueFactory()
        address = geography_factories.AddressFactory()
        oa = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer, address=address)

        with assert_no_difference(OffererAddress):
            oa = get_or_create_offerer_address(oa.offererId, oa.addressId, oa.label)
            db.session.commit()

        assert oa.offerer == venue.managingOfferer
        assert oa.address == address


def build_address():
    return geography_factories.AddressFactory(
        street=TestingBackend.address.street,
        postalCode=TestingBackend.address.postal_code,
        city=TestingBackend.address.city,
        inseeCode=TestingBackend.address.insee_code,
    )


class TransformVirtualVenueTest:
    def test_transform_virtual_venue(self):
        build_address()
        venue = offerers_factories.VirtualVenueFactory(managingOfferer__siren="012345678")

        transform_virtual_venue(venue, False)

        db.session.refresh(venue)

        assert venue.offererAddress
        assert venue.siret
        assert venue.name == "MINISTERE DE LA CULTURE"
        assert not venue.isVirtual
        assert not venues_from_offerers_with_one_unique_virtual_venue().all()

    def test_does_not_transform_physical_venue(self):
        build_address()
        venue = offerers_factories.VenueFactory(managingOfferer__siren="012345678")

        with pytest.raises(NotAVirtualVenue):
            transform_virtual_venue(venue, False)

        assert not venue.isVirtual

    @patch("pcapi.connectors.api_adresse.get_address")
    def test_does_not_transform_virtual_venue_if_no_address_found(self, mock_get_ban_address):
        venue = offerers_factories.VirtualVenueFactory(managingOfferer__siren="012345678")

        mock_get_ban_address.side_effect = api_adresse.NoResultException

        with pytest.raises(FetchAddressError):
            transform_virtual_venue(venue, False)

        assert venue.isVirtual

    def test_does_not_transform_virtual_venue_if_offerer_has_no_siren(self):
        build_address()
        venue = offerers_factories.VirtualVenueFactory(managingOfferer__siren="")

        with pytest.raises(MissingSirenError):
            transform_virtual_venue(venue, False)

        assert venue.isVirtual


class TransformVenuesFromOfferersWithOneUniqueVirtualVenueTest:
    def test_transform_venues(self):
        build_address()

        # for each offerer:
        # one virtual venue (no more, no less) -> should be updated
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()
        expected_venues = [
            offerers_factories.VirtualVenueFactory(managingOfferer=offerer1),
            offerers_factories.VirtualVenueFactory(managingOfferer=offerer2),
        ]

        # one virtual venue and one physical venue -> none should be updated
        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer2)
        offerers_factories.VenueFactory(managingOfferer=offerer2)

        # one virtual venue and no physical venue -> should not be updated
        offerer3 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(managingOfferer=offerer3)

        transformed_venue_ids = transform_venues_from_offerers_with_one_unique_virtual_venue(False)
        assert transformed_venue_ids == {v.id for v in expected_venues}

        for venue in Venue.query.filter(Venue.id.in_(transformed_venue_ids)).all():
            assert venue.offererAddress
            assert venue.siret
            assert not venue.isVirtual

    def test_rollback_changes_for_one_venue_if_error_and_updated_others(self):
        def assert_updated(venue):
            assert venue.offererAddress
            assert venue.siret
            assert not venue.isVirtual

        def assert_not_updated(venue):
            assert not venue.offererAddress
            assert not venue.siret
            assert venue.isVirtual

        build_address()

        # for each offerer:
        # one virtual venue (no more, no less) -> should be updated
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()
        offerer3 = offerers_factories.OffererFactory()
        expected_venues = [
            offerers_factories.VirtualVenueFactory(managingOfferer=offerer1),
            offerers_factories.VirtualVenueFactory(managingOfferer=offerer2),
            offerers_factories.VirtualVenueFactory(managingOfferer=offerer3),
        ]

        original_backend = get_backend()

        path = "pcapi.scripts.transform_virtual_venues.main.get_backend"
        with patch(path) as mock_transform_virtual_venue:
            # first venue should be updated
            # second should not because of error
            # third should be updated
            mock_transform_virtual_venue.side_effect = [
                original_backend,
                RuntimeError("test"),
                original_backend,
            ]

            with pytest.raises(RuntimeError):
                transform_venues_from_offerers_with_one_unique_virtual_venue(False)

            # Assert updated
            assert_updated(expected_venues[0])

            # Assert not updated
            assert_not_updated(expected_venues[1])
            assert_not_updated(expected_venues[2])
