from unittest.mock import patch

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.scripts.change_virtual_to_physical.main import HeadQuarterInfo
from pcapi.scripts.change_virtual_to_physical.main import get_offerer_with_one_virtual_venue_query
from pcapi.scripts.change_virtual_to_physical.main import transform_offerer_unique_virtual_venue_to_physical_venue
from pcapi.scripts.change_virtual_to_physical.main import transform_virtual_venue_to_physical_venue


pytestmark = pytest.mark.usefixtures("db_session")


class GetOffererWithOneVirtualVenueQueryTest:
    def test_one_existing_unique_virtual_offerer(self):
        virtual_venue = offerers_factories.VenueFactory(isVirtual=True, siret=None, comment="virtual")

        offerers = get_offerer_with_one_virtual_venue_query().all()
        assert len(offerers) == 1
        assert offerers[0].id == virtual_venue.managingOffererId

    def test_returns_nothing_if_multiple_virtual_venues(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory.create_batch(
            2, managingOfferer=offerer, isVirtual=True, siret=None, comment="virtual"
        )

        offerers = get_offerer_with_one_virtual_venue_query().all()
        assert not offerers

    def test_returns_offerers(self):
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()

        offerers_factories.VenueFactory(managingOfferer=offerer1, isVirtual=True, siret=None, comment="virtual")
        offerers_factories.VenueFactory(managingOfferer=offerer2, isVirtual=True, siret=None, comment="virtual")

        # venues from offerers that have one (not more) virtual venue
        expected_offerers = [offerer1, offerer2]

        # more than one virtual venue: should not match
        offerer3 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory.create_batch(
            2, managingOfferer=offerer3, isVirtual=True, siret=None, comment="virtual"
        )

        # no virtual venue: should not match
        offerer4 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer4)

        # one virtual and at least one physical venue: should not match
        offerer5 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(managingOfferer=offerer5, isVirtual=True, siret=None, comment="virtual")
        offerers_factories.VenueFactory(managingOfferer=offerer5, isVirtual=False)

        offerers = get_offerer_with_one_virtual_venue_query().all()
        assert len(offerers) == len(expected_offerers)
        assert {v.id for v in offerers} == {v.id for v in expected_offerers}


class TransformVirtualVenueToPhysicalVenueTest:
    @patch("pcapi.scripts.change_virtual_to_physical.main.EntrepriseWithHeadQuartersBackend.get_head_quarter_info")
    def test_transform_virtual_venue_to_physical_venue(self, get_head_quarter_info):
        educational_domain = educational_factories.EducationalDomainFactory(name="Arts numériques")
        get_head_quarter_info.return_value = HeadQuarterInfo(
            siret="1234567891234",
            diffusible=True,
            active=True,
            enseigne="Enseigne",
            raison_sociale="Raison sociale",
        )

        venue = offerers_factories.VenueFactory(
            name="venue numérique",
            publicName="Rezeed",
            managingOfferer__siren="123456789",
            isVirtual=True,
            siret=None,
            comment="virtual",
            venueTypeCode=VenueTypeCode.DIGITAL,
        )
        author = users_factories.UserFactory()

        transform_virtual_venue_to_physical_venue(venue, venue.managingOfferer, author)

        db.session.refresh(venue)

        assert venue.siret == "1234567891234"
        assert venue.name == "Raison sociale"
        assert venue.publicName == "Raison sociale"
        assert not venue.isVirtual
        assert venue.activity == Activity.OTHER
        assert venue.venueTypeCode == VenueTypeCode.OTHER
        assert venue.collectiveDomains == [educational_domain]

        get_head_quarter_info.assert_called_once_with("123456789")

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUser == author
        assert action.user is None
        assert action.offerer is None
        assert action.venue == venue
        assert action.extraData["modified_info"] == {
            "activity": {"new_info": Activity.OTHER.name, "old_info": Activity.ARTS_EDUCATION.name},
            "isPermanent": {"new_info": True, "old_info": False},
            "isVirtual": {"new_info": False, "old_info": True},
            "siret": {"new_info": venue.siret, "old_info": None},
            "venueTypeCode": {"new_info": VenueTypeCode.OTHER.name, "old_info": VenueTypeCode.DIGITAL.name},
            "name": {"new_info": "Raison sociale", "old_info": "venue numérique"},
            "publicName": {"new_info": "Raison sociale", "old_info": "Rezeed"},
        }

    @patch("pcapi.scripts.change_virtual_to_physical.main.EntrepriseWithHeadQuartersBackend.get_head_quarter_info")
    def test_transform_virtual_venue_to_physical_venue_when_no_raison_sociale_or_enseigne(
        self, get_head_quarter_info_mock
    ):
        educational_factories.EducationalDomainFactory(name="Arts numériques")
        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="012345678",
            name="venue numérique",
            publicName="Rezeed",
            isVirtual=True,
            siret=None,
            comment="virtual",
        )
        get_head_quarter_info_mock.return_value = HeadQuarterInfo(
            diffusible=True, active=True, siret="78467169500087", raison_sociale=None, enseigne=None
        )

        author = users_factories.UserFactory()

        transform_virtual_venue_to_physical_venue(venue, venue.managingOfferer, author)

        db.session.refresh(venue)

        assert venue.offererAddress
        assert venue.siret
        assert venue.name == venue.managingOfferer.name
        assert venue.publicName == venue.managingOfferer.name
        assert not venue.isVirtual
        assert not get_offerer_with_one_virtual_venue_query().all()

    @patch("pcapi.scripts.change_virtual_to_physical.main.EntrepriseWithHeadQuartersBackend.get_head_quarter_info")
    def test_transform_virtual_venue_to_physical_venue_siret_not_diffusible(self, get_head_quarter_info_mock):
        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="012345678", isVirtual=True, siret=None, comment="virtual"
        )
        educational_domain = educational_factories.EducationalDomainFactory(name="Arts numériques")
        get_head_quarter_info_mock.return_value = HeadQuarterInfo(
            diffusible=False, active=True, siret="78467169500087", raison_sociale=None, enseigne=None
        )
        author = users_factories.UserFactory()

        transform_virtual_venue_to_physical_venue(venue, venue.managingOfferer, author)

        db.session.refresh(venue)

        assert venue.siret == "78467169500087"
        assert venue.name == venue.managingOfferer.name
        assert venue.publicName == venue.managingOfferer.name
        assert not venue.isVirtual
        assert venue.activity == Activity.OTHER
        assert venue.venueTypeCode == VenueTypeCode.OTHER
        assert venue.collectiveDomains == [educational_domain]
        assert not get_offerer_with_one_virtual_venue_query().all()


class TransformVenuesFromOfferersWithOneUniqueVirtualVenueTest:
    @patch("pcapi.scripts.change_virtual_to_physical.main.transform_virtual_venue_to_physical_venue")
    def test_transform_venues(self, transform_virtual_venue_to_physical_venue_mock):
        # for each offerer:
        # one virtual venue (no more, no less) -> should be updated
        offerer1 = offerers_factories.OffererFactory()

        virtual_venue_that_should_be_transformed = offerers_factories.VenueFactory(
            managingOfferer=offerer1, isVirtual=True, siret=None, comment="virtual"
        )

        # one virtual venue and one physical venue -> none should be updated
        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(managingOfferer=offerer2, isVirtual=True, siret=None, comment="virtual")
        offerers_factories.VenueFactory(managingOfferer=offerer2, isVirtual=False)

        # one physical venue and no virtual venue -> should not be updated
        offerer3 = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(managingOfferer=offerer3)
        author = users_factories.UserFactory()

        transform_offerer_unique_virtual_venue_to_physical_venue(author)
        transform_virtual_venue_to_physical_venue_mock.assert_called_once_with(
            virtual_venue_that_should_be_transformed, offerer1, author
        )
