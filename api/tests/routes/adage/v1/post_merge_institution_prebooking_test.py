import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.models import db


@pytest.fixture(name="eac_client")
def eac_client_fixture(client):
    return client.with_eac_token()


@pytest.fixture(name="current_year")
def current_year_fixture():
    return factories.EducationalCurrentYearFactory()


@pytest.fixture(name="booking")
def booking_fixture(current_year):
    return factories.CollectiveBookingFactory(educationalYear=current_year)


@pytest.mark.usefixtures("db_session")
class PostMergeInstitutionPrebookingTest:
    """Merge institutions prebooking: move bookings from an institution
    to another.
    """

    def test_merge_institution_prebooking(self, eac_client, booking) -> None:
        destination_institution = factories.EducationalInstitutionFactory()

        body = {
            "source_uai": booking.educationalInstitution.institutionId,
            "destination_uai": destination_institution.institutionId,
            "bookings_ids": [booking.id],
        }

        response = eac_client.post("/adage/v1/prebookings/move", json=body)
        assert response.status_code == 204

        db.session.refresh(booking)

        assert booking.educationalInstitution.institutionId == destination_institution.institutionId
        assert booking.collectiveStock.collectiveOffer.institution == destination_institution

    def test_merge_institution_prebooking_institution_destination_in_adage_only(self, eac_client, booking) -> None:
        destination_uai = "0470009E"
        assert booking.educationalInstitution.institutionId != destination_uai

        body = {
            "source_uai": booking.educationalInstitution.institutionId,
            "destination_uai": destination_uai,
            "bookings_ids": [booking.id],
        }

        response = eac_client.post("/adage/v1/prebookings/move", json=body)
        assert response.status_code == 204

        # first: existing one created by the booking, second: the new
        # one created by the api call
        assert models.EducationalInstitution.query.count() == 2
        assert destination_uai in {inst.institutionId for inst in models.EducationalInstitution.query.all()}

        db.session.refresh(booking)

        # booking and its offer should be attached to the newly created
        # institution
        assert booking.educationalInstitution.institutionId == destination_uai
        assert booking.collectiveStock.collectiveOffer.institution.institutionId == destination_uai

    def test_merge_institution_prebooking_institution_destination_dont_exist(self, eac_client, current_year) -> None:
        institution_source = factories.EducationalInstitutionFactory()

        body = {
            "source_uai": institution_source.institutionId,
            "destination_uai": "oh no",
            "bookings_ids": [1, 2, 3],
        }

        response = eac_client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 404
        assert response.json == {"destination_uai": "not found"}

    def test_merge_institution_prebooking_institution_source_not_found(self, eac_client) -> None:
        body = {
            "source_uai": "oh no nono nonono",
            "destination_uai": "the destination",
            "bookings_ids": [1, 2, 3],
        }

        response = eac_client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 404
        assert response.json == {"code": "Source institution not found"}

    def test_merge_institution_prebooking_institution_authentification_failed(self, client) -> None:
        body = {
            "source_uai": "1",
            "destination_uai": "2",
            "bookings_ids": [1],
        }

        response = client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 401
        assert response.json == {"Authorization": ["Missing API key"]}
