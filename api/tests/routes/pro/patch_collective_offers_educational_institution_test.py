import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_offer_institution_link(self, client):
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

    def test_change_offer_institution_link(self, client):
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

    def test_delete_offer_institution_link(self, client):
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

    def test_add_institution_link_on_pending_offer(self, client):
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


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_offer_not_found(self, client):
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

    def test_institution_not_found(self, client):
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
class Returns403Test:
    def test_change_institution_on_uneditable_offer_booking_confirmed(self, client):
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

    def test_change_institution_on_uneditable_offer_booking_reimbused(self, client):
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

    def test_change_institution_on_uneditable_offer_booking_used(self, client):
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
