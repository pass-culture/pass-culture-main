from typing import Any

import pytest

from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_settings
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
@override_settings(ADAGE_API_URL="https://adage_base_url")
class Returns200Test:
    def test_create_offer_institution_link(self, client: Any) -> None:
        # Given
        institution = EducationalInstitutionFactory()
        stock = CollectiveStockFactory()
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution.id, "isCreatingOffer": True}
        response = client.patch(f"/collective/offers/{humanize(offer.id)}/educational_institution", json=data)

        # Then
        assert response.status_code == 200
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution

        expected_payload = serialize_collective_offer(offer)
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/offre-assoc"

    def test_change_offer_institution_link(self, client: Any) -> None:
        # Given
        institution1 = EducationalInstitutionFactory()
        stock = CollectiveStockFactory(collectiveOffer__institution=institution1)
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = EducationalInstitutionFactory()

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id, "isCreatingOffer": False}
        response = client.patch(f"/collective/offers/{humanize(offer.id)}/educational_institution", json=data)

        # Then
        assert response.status_code == 200
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution2

    def test_delete_offer_institution_link(self, client: Any) -> None:
        # Given
        institution = EducationalInstitutionFactory()
        stock = CollectiveStockFactory(collectiveOffer__institution=institution)
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": None, "isCreatingOffer": False}
        response = client.patch(f"/collective/offers/{humanize(offer.id)}/educational_institution", json=data)

        # Then
        assert response.status_code == 200
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution is None

        assert len(adage_api_testing.adage_requests) == 0

    def test_add_institution_link_on_pending_offer(self, client: Any) -> None:
        # Given
        institution = EducationalInstitutionFactory()
        stock = CollectiveStockFactory(collectiveOffer__validation="PENDING")
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution.id, "isCreatingOffer": True}
        response = client.patch(f"/collective/offers/{humanize(offer.id)}/educational_institution", json=data)

        # Then
        assert response.status_code == 200
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution

        assert len(adage_api_testing.adage_requests) == 0


@pytest.mark.usefixtures("db_session")
@override_settings(ADAGE_API_URL="https://adage_base_url")
class Returns404Test:
    def test_offer_not_found(self, client: Any) -> None:
        # Given
        institution = EducationalInstitutionFactory()
        stock = CollectiveStockFactory()
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution.id, "isCreatingOffer": False}
        response = client.patch("/collective/offers/0/educational_institution", json=data)

        # Then
        assert response.status_code == 404
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == None

    def test_institution_not_found(self, client: Any) -> None:
        # Given
        stock = CollectiveStockFactory()
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": 0, "isCreatingOffer": False}
        response = client.patch(f"/collective/offers/{humanize(offer.id)}/educational_institution", json=data)

        # Then
        assert response.status_code == 404
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == None


@pytest.mark.usefixtures("db_session")
@override_settings(ADAGE_API_URL="https://adage_base_url")
class Returns403Test:
    def test_change_institution_on_uneditable_offer_booking_confirmed(self, client: Any) -> None:
        # Given
        institution1 = EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            collectiveStock__collectiveOffer__institution=institution1, status=CollectiveBookingStatus.CONFIRMED
        )
        offer = booking.collectiveStock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = EducationalInstitutionFactory()

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id, "isCreatingOffer": False}
        response = client.patch(f"/collective/offers/{humanize(offer.id)}/educational_institution", json=data)

        # Then
        assert response.status_code == 403
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution1

    def test_change_institution_on_uneditable_offer_booking_reimbused(self, client: Any) -> None:
        # Given
        institution1 = EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            collectiveStock__collectiveOffer__institution=institution1, status=CollectiveBookingStatus.REIMBURSED
        )
        offer = booking.collectiveStock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = EducationalInstitutionFactory()

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id, "isCreatingOffer": False}
        response = client.patch(f"/collective/offers/{humanize(offer.id)}/educational_institution", json=data)

        # Then
        assert response.status_code == 403
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution1

    def test_change_institution_on_uneditable_offer_booking_used(self, client: Any) -> None:
        # Given
        institution1 = EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            collectiveStock__collectiveOffer__institution=institution1, status=CollectiveBookingStatus.USED
        )
        offer = booking.collectiveStock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = EducationalInstitutionFactory()

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id, "isCreatingOffer": False}
        response = client.patch(f"/collective/offers/{humanize(offer.id)}/educational_institution", json=data)

        # Then
        assert response.status_code == 403
        offer_db = CollectiveOffer.query.filter(CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution1
