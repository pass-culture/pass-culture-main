from typing import Any

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as adage_api_testing
from pcapi.core.offerers import factories as offerers_factories


STATUSES_ALLOWING_EDIT_INSTITUTION = (models.CollectiveOfferDisplayedStatus.DRAFT,)

STATUSES_NOT_ALLOWING_EDIT_INSTITUTION = tuple(
    set(models.CollectiveOfferDisplayedStatus)
    - {*STATUSES_ALLOWING_EDIT_INSTITUTION, models.CollectiveOfferDisplayedStatus.INACTIVE}
)


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
class Returns200Test:
    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_ALLOWING_EDIT_INSTITUTION)
    def test_change_institution_allowed_action(self, client, status) -> None:
        institution1 = factories.EducationalInstitutionFactory()
        offer = factories.create_collective_offer_by_status(status=status, institution=institution1)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = factories.EducationalInstitutionFactory()

        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.institution == institution2


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
class Returns404Test:
    def test_offer_not_found(self, client: Any) -> None:
        # Given
        institution = factories.EducationalInstitutionFactory()
        stock = factories.CollectiveStockFactory()
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution.id}
        response = client.patch("/collective/offers/0/educational_institution", json=data)

        # Then
        assert response.status_code == 404
        offer_db = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer_db.institution is None

    def test_institution_not_found(self, client: Any) -> None:
        offer = factories.DraftCollectiveOfferFactory()
        offer.institution = None
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": 0}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        assert response.status_code == 404
        offer_db = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer_db.institution is None


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
class Returns403Test:
    def test_change_institution_on_uneditable_offer_booking_confirmed(self, client: Any) -> None:
        # Given
        institution1 = factories.EducationalInstitutionFactory()
        booking = factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__institution=institution1, status=models.CollectiveBookingStatus.CONFIRMED
        )
        offer = booking.collectiveStock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = factories.EducationalInstitutionFactory()

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        # Then
        assert response.status_code == 403
        offer_db = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution1

    def test_change_institution_on_uneditable_offer_booking_reimbused(self, client: Any) -> None:
        # Given
        institution1 = factories.EducationalInstitutionFactory()
        booking = factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__institution=institution1, status=models.CollectiveBookingStatus.REIMBURSED
        )
        offer = booking.collectiveStock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = factories.EducationalInstitutionFactory()

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        # Then
        assert response.status_code == 403
        offer_db = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution1

    def test_change_institution_on_uneditable_offer_booking_used(self, client: Any) -> None:
        # Given
        institution1 = factories.EducationalInstitutionFactory()
        booking = factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__institution=institution1, status=models.CollectiveBookingStatus.USED
        )
        offer = booking.collectiveStock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = factories.EducationalInstitutionFactory()

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        # Then
        assert response.status_code == 403
        offer_db = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer_db.institution == institution1

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_NOT_ALLOWING_EDIT_INSTITUTION)
    def test_change_institution_unallowed_action(self, client, status) -> None:
        institution1 = factories.EducationalInstitutionFactory()
        offer = factories.create_collective_offer_by_status(status=status, institution=institution1)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = factories.EducationalInstitutionFactory()

        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        assert response.status_code == 403
        assert response.json == {"offer": ["Cette action n'est pas autorisée sur cette offre"]}
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.institution == institution1

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_change_institution_ended(self, client) -> None:
        institution1 = factories.EducationalInstitutionFactory()
        offer = factories.EndedCollectiveOfferFactory(booking_is_confirmed=True, institution=institution1)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)
        institution2 = factories.EducationalInstitutionFactory()

        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution2.id}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        assert response.status_code == 403
        assert response.json == {"offer": ["Cette action n'est pas autorisée sur cette offre"]}
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.institution == institution1

    def test_add_institution_link_on_pending_offer(self, client: Any) -> None:
        # Given
        institution = factories.EducationalInstitutionFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer__validation="PENDING")
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution.id}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        # Then
        assert response.status_code == 403
        offer_db = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer_db.institution is None

        assert len(adage_api_testing.adage_requests) == 0

    def test_offer_institution_link_institution_not_active(self, client: Any) -> None:
        # Given
        institution = factories.EducationalInstitutionFactory(isActive=False)
        stock = factories.CollectiveStockFactory()
        offer = stock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"educationalInstitutionId": institution.id}
        response = client.patch(f"/collective/offers/{offer.id}/educational_institution", json=data)

        # Then
        assert response.status_code == 403
