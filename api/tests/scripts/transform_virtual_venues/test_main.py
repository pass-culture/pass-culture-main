import contextlib
import logging
from unittest.mock import patch

import pytest

from pcapi.connectors import api_adresse
import pcapi.core.geography.factories as geography_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.scripts.transform_virtual_venues.main import HeadQuarterInfo
from pcapi.scripts.transform_virtual_venues.main import MissingSirenError
from pcapi.scripts.transform_virtual_venues.main import SiretNotActiveOrNotDiffusible
from pcapi.scripts.transform_virtual_venues.main import get_offerer_with_one_virtual_venue_query
from pcapi.scripts.transform_virtual_venues.main import transform_offerer_unique_virtual_venue_to_physical_venue
from pcapi.scripts.transform_virtual_venues.main import transform_virtual_venue_to_physical_venue


pytestmark = pytest.mark.usefixtures("db_session")


class GetOffererWithOneVirtualVenueQueryTest:
    def test_one_existing_unique_virtual_offerer(self):
        virtual_venue = offerers_factories.VirtualVenueFactory()

        offerers = get_offerer_with_one_virtual_venue_query().all()
        assert len(offerers) == 1
        assert offerers[0].id == virtual_venue.managingOffererId

    def test_returns_nothing_if_multiple_virtual_venues(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory.create_batch(2, managingOfferer=offerer)

        offerers = get_offerer_with_one_virtual_venue_query().all()
        assert not offerers

    def test_returns_offerers(self):
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()

        offerers_factories.VirtualVenueFactory(managingOfferer=offerer1)
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer2)

        # venues from offerers that have one (not more) virtual venue
        expected_offerers = [offerer1, offerer2]

        # more than one virtual venue: should not match
        offerer3 = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory.create_batch(2, managingOfferer=offerer3)

        # no virtual venue: should not match
        offerer4 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer4)

        # one virtual and at least one physical venue: should not match
        offerer4 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer4)

        offerers = get_offerer_with_one_virtual_venue_query().all()
        assert len(offerers) == len(expected_offerers)
        assert {v.id for v in offerers} == {v.id for v in expected_offerers}


def build_address(offerer: Offerer):
    return geography_factories.AddressFactory(street=offerer.street, postalCode=offerer.postalCode, city=offerer.city)


class TransformVirtualVenueToPhysicalVenueTest:
    def test_transform_virtual_venue_to_physical_venue(self):
        venue = offerers_factories.VirtualVenueFactory(managingOfferer__siren="012345678")
        build_address(venue.managingOfferer)

        transform_virtual_venue_to_physical_venue(venue, venue.managingOfferer, False)

        db.session.refresh(venue)

        assert venue.offererAddress
        assert venue.siret
        assert venue.name == "Raison sociale"
        assert venue.publicName == "Enseigne"
        assert venue.venueTypeCode == VenueTypeCode.ADMINISTRATIVE
        assert not venue.isVirtual
        assert not get_offerer_with_one_virtual_venue_query().all()

    @patch("pcapi.scripts.transform_virtual_venues.main.get_head_quarter_info")
    def test_transform_virtual_venue_to_physical_venue_when_no_raison_sociale_or_enseigne(
        self, get_head_quarter_info_mock
    ):
        venue = offerers_factories.VirtualVenueFactory(managingOfferer__siren="012345678", publicName=None)
        build_address(venue.managingOfferer)

        get_head_quarter_info_mock.return_value = HeadQuarterInfo(
            diffusible=True, active=True, siret="78467169500087", raison_sociale=None, enseigne=None
        )

        transform_virtual_venue_to_physical_venue(venue, venue.managingOfferer, False)

        db.session.refresh(venue)

        assert venue.offererAddress
        assert venue.siret
        assert venue.name == venue.managingOfferer.name
        assert venue.publicName == None
        assert not venue.isVirtual
        assert not get_offerer_with_one_virtual_venue_query().all()

    @patch("pcapi.scripts.transform_virtual_venues.main.get_head_quarter_info")
    @pytest.mark.parametrize(
        "head_quarter_info",
        [
            HeadQuarterInfo(diffusible=False, active=True, siret="78467169500087", raison_sociale=None, enseigne=None),
            HeadQuarterInfo(diffusible=True, active=False, siret="78467169500087", raison_sociale=None, enseigne=None),
        ],
    )
    def test_transform_virtual_venue_to_physical_venue_should_raise_because_not_diffusible_or_not_active(
        self, get_head_quarter_info_mock, head_quarter_info
    ):
        venue = offerers_factories.VirtualVenueFactory(managingOfferer__siren="012345678")
        build_address(venue.managingOfferer)

        get_head_quarter_info_mock.return_value = head_quarter_info

        with pytest.raises(SiretNotActiveOrNotDiffusible):
            transform_virtual_venue_to_physical_venue(venue, venue.managingOfferer, False)

        db.session.refresh(venue)

        assert not venue.offererAddress
        assert not venue.siret
        assert venue.isVirtual
        assert get_offerer_with_one_virtual_venue_query().all()

    def test_transform_virtual_venue_to_physical_venue_should_raise_because_siren_is_missing(self):
        offerer = offerers_factories.OffererFactory()
        offerer.siren = None
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        build_address(venue.managingOfferer)

        with pytest.raises(MissingSirenError):
            transform_virtual_venue_to_physical_venue(venue, venue.managingOfferer, False)

        db.session.refresh(venue)

        assert not venue.offererAddress
        assert not venue.siret
        assert venue.isVirtual
        assert get_offerer_with_one_virtual_venue_query().all()


class TransformVenuesFromOfferersWithOneUniqueVirtualVenueTest:

    @patch("pcapi.scripts.transform_virtual_venues.main.transform_virtual_venue_to_physical_venue")
    @patch("pcapi.scripts.transform_virtual_venues.main.delete_venue")
    def test_transform_venues(self, delete_venue_mock, transform_virtual_venue_to_physical_venue_mock):
        # for each offerer:
        # one virtual venue (no more, no less) -> should be updated
        offerer1 = offerers_factories.OffererFactory()
        build_address(offerer1)
        rejected_offerer = offerers_factories.OffererFactory(validationStatus=ValidationStatus.REJECTED)

        virtual_venue_that_should_be_transformed = offerers_factories.VirtualVenueFactory(managingOfferer=offerer1)
        virtual_venue_that_should_be_deleted = offerers_factories.VirtualVenueFactory(managingOfferer=rejected_offerer)

        # one virtual venue and one physical venue -> none should be updated
        offerer4 = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer4)
        offerers_factories.VenueFactory(managingOfferer=offerer4)

        # one virtual venue and no physical venue -> should not be updated
        offerer3 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(managingOfferer=offerer3)

        transform_offerer_unique_virtual_venue_to_physical_venue(False)
        delete_venue_mock.assert_called_once_with(virtual_venue_that_should_be_deleted.id)
        transform_virtual_venue_to_physical_venue_mock.assert_called_once_with(
            virtual_venue_that_should_be_transformed, offerer1, dry_run=False
        )

    @patch("pcapi.scripts.transform_virtual_venues.main.transform_virtual_venue_to_physical_venue")
    @pytest.mark.parametrize(
        "exception,expected_logging_level,expected_message",
        [
            (MissingSirenError(), logging.WARNING, "Offerer does not have a SIREN"),
            (SiretNotActiveOrNotDiffusible(), logging.WARNING, "Siret info cannot be used"),
            (api_adresse.AdresseApiException(), logging.WARNING, "Failed to found address on BAN API"),
            (Exception(), logging.ERROR, "Virtual Venue could not be transformed because of unexpected error"),
        ],
    )
    def test_transform_venues(
        self,
        transform_virtual_venue_to_physical_venue_mock,
        caplog,
        exception,
        expected_logging_level,
        expected_message,
    ):
        # for each offerer:
        # one virtual venue (no more, no less) -> should be updated
        offerer1 = offerers_factories.OffererFactory()
        build_address(offerer1)

        offerers_factories.VirtualVenueFactory(managingOfferer=offerer1)

        transform_virtual_venue_to_physical_venue_mock.side_effect = exception

        with caplog.at_level(expected_logging_level):
            transform_offerer_unique_virtual_venue_to_physical_venue(False)

        assert caplog.records[0].message == expected_message
