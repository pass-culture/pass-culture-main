import pytest

from pcapi.core.educational import models
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import ConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.testing import assert_no_duplicated_queries

from tests.routes.adage.v1.conftest import expected_serialized_prebooking


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_collective_bookings(self, client) -> None:
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        booking2 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()

        with assert_no_duplicated_queries():
            response = client.get(
                f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings"
            )

        assert response.status_code == 200
        assert response.json == {
            "prebookings": [
                expected_serialized_prebooking(booking1),
                expected_serialized_prebooking(booking2),
            ]
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_get_collective_bookings_with_oa(self, client):
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking = ConfirmedCollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.ADDRESS,
            collectiveStock__collectiveOffer__offererAddress=None,
            collectiveStock__collectiveOffer__locationComment=None,
        )
        offer = booking.collectiveStock.collectiveOffer
        offer.offererAddress = offer.venue.offererAddress

        with assert_no_duplicated_queries():
            response = client.with_eac_token().get(
                f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings"
            )

        assert response.status_code == 200
        assert response.json == {
            "prebookings": [
                {
                    **expected_serialized_prebooking(booking),
                    "address": offer.offererAddress.address.fullAddress,
                }
            ]
        }

    def test_get_collective_bookings_filter_UAI(self, client) -> None:
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        other_educational_institution = EducationalInstitutionFactory(institutionId="Pouet")
        CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=other_educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()

        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings"
        )

        assert response.status_code == 200
        assert response.json == {"prebookings": [expected_serialized_prebooking(booking1)]}

    def test_get_collective_bookings_filter_year_id(self, client) -> None:
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        other_educational_year = EducationalYearFactory(adageId="Pouet")
        CollectiveBookingFactory(
            educationalYear=other_educational_year,
            educationalInstitution=educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()

        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings"
        )

        assert response.status_code == 200
        assert response.json == {"prebookings": [expected_serialized_prebooking(booking1)]}

    def test_get_collective_bookings_filter_redactor_email(self, client) -> None:
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="PENDING",
            educationalRedactor__email="redactor@example.com",
        )

        client = client.with_eac_token()

        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings?redactorEmail={booking1.educationalRedactor.email}"
        )

        assert response.status_code == 200
        assert response.json == {"prebookings": [expected_serialized_prebooking(booking1)]}

    def test_get_collective_bookings_filter_status(self, client) -> None:
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        other_educational_year = EducationalYearFactory(adageId="Pouet")
        CollectiveBookingFactory(
            educationalYear=other_educational_year,
            educationalInstitution=educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()

        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings?status=CONFIRMED"
        )

        assert response.status_code == 200
        assert response.json == {"prebookings": [expected_serialized_prebooking(booking1)]}
