import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.models import db

from tests.conftest import TestClient


NOT_ALLOWED_STATUS = [
    status for status in models.CollectiveBookingStatus if status != models.CollectiveBookingStatus.PENDING
]


@pytest.mark.usefixtures("db_session")
class PostMergeInstitutionPrebookingTest:
    """Merge institutions prebooking: move bookings from an institution
    to another.
    """

    @pytest.mark.parametrize("status", NOT_ALLOWED_STATUS)
    def test_merge_institution_prebooking(self, client: TestClient, status: models.CollectiveBookingStatus):
        current_year = factories.EducationalCurrentYearFactory()
        source_institution = factories.EducationalInstitutionFactory()
        booking = factories.CollectiveBookingFactory(
            educationalYear=current_year,
            educationalInstitution=source_institution,
            collectiveStock__collectiveOffer__institution=source_institution,
            status=status,
        )
        pending_booking = factories.PendingCollectiveBookingFactory(
            educationalYear=current_year,
            educationalInstitution=source_institution,
            collectiveStock__collectiveOffer__institution=source_institution,
        )
        destination_institution = factories.EducationalInstitutionFactory()

        body = {
            "source_uai": source_institution.institutionId,
            "destination_uai": destination_institution.institutionId,
            "bookings_ids": [booking.id, pending_booking.id],
        }

        response = client.with_eac_token().post("/adage/v1/prebookings/move", json=body)
        assert response.status_code == 200
        assert response.json == {"movedBookingIds": [pending_booking.id], "notMovedBookingIds": [booking.id]}

        db.session.refresh(booking)
        db.session.refresh(pending_booking)

        assert booking.educationalInstitution.institutionId == source_institution.institutionId
        assert booking.collectiveStock.collectiveOffer.institution == source_institution

        assert pending_booking.educationalInstitution.institutionId == destination_institution.institutionId
        assert pending_booking.collectiveStock.collectiveOffer.institution == destination_institution

    def test_merge_institution_prebooking_institution_destination_in_adage_only(self, client: TestClient):
        current_year = factories.EducationalCurrentYearFactory()
        booking = factories.PendingCollectiveBookingFactory(educationalYear=current_year)
        destination_uai = "0470009E"
        assert booking.educationalInstitution.institutionId != destination_uai

        body = {
            "source_uai": booking.educationalInstitution.institutionId,
            "destination_uai": destination_uai,
            "bookings_ids": [booking.id],
        }

        response = client.with_eac_token().post("/adage/v1/prebookings/move", json=body)
        assert response.status_code == 200
        assert response.json == {"movedBookingIds": [booking.id], "notMovedBookingIds": []}

        # first: existing one created by the booking, second: the new
        # one created by the api call
        assert db.session.query(models.EducationalInstitution).count() == 2
        assert destination_uai in {inst.institutionId for inst in db.session.query(models.EducationalInstitution).all()}

        db.session.refresh(booking)

        # booking and its offer should be attached to the newly created
        # institution
        assert booking.educationalInstitution.institutionId == destination_uai
        assert booking.collectiveStock.collectiveOffer.institution.institutionId == destination_uai

    def test_merge_institution_prebooking_institution_destination_dont_exist(self, client: TestClient):
        factories.EducationalCurrentYearFactory()
        institution_source = factories.EducationalInstitutionFactory()

        body = {
            "source_uai": institution_source.institutionId,
            "destination_uai": "oh no",
            "bookings_ids": [1, 2, 3],
        }

        response = client.with_eac_token().post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 404
        assert response.json == {"destination_uai": "not found"}

    def test_merge_institution_prebooking_institution_source_not_found(self, client: TestClient):
        body = {
            "source_uai": "oh no nono nonono",
            "destination_uai": "the destination",
            "bookings_ids": [1, 2, 3],
        }

        response = client.with_eac_token().post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 404
        assert response.json == {"code": "Source institution not found"}

    def test_merge_institution_prebooking_institution_authentification_failed(self, client: TestClient):
        body = {
            "source_uai": "1",
            "destination_uai": "2",
            "bookings_ids": [1],
        }

        response = client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 401
        assert response.json == {"Authorization": ["Missing API key"]}
