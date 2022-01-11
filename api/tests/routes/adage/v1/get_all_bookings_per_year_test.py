import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_all_bookings_per_year(self, client) -> None:
        educationalYear = EducationalYearFactory()
        educationalInstitution = EducationalInstitutionFactory()
        other_educational_institution = EducationalInstitutionFactory(institutionId="institutionId")
        other_educational_year = EducationalYearFactory(adageId="adageId")
        booking1 = EducationalBookingFactory(
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=educationalInstitution,
            status="CONFIRMED",
        )
        booking2 = EducationalBookingFactory(
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=other_educational_institution,
            status="PENDING",
        )
        EducationalBookingFactory(educationalBooking__educationalYear=other_educational_year)
        EducationalBookingFactory(educationalBooking__educationalInstitution=other_educational_institution)

        client = client.with_eac_token()
        response = client.get(f"/adage/v1/years/{booking1.educationalBooking.educationalYear.adageId}/prebookings")

        assert response.status_code == 200

        assert response.json == {
            "bookings": [
                {
                    "UAICode": educationalInstitution.institutionId,
                    "status": "CONFIRMED",
                    "confirmationLimitDate": format_into_utc_date(booking1.educationalBooking.confirmationLimitDate),
                    "totalAmount": booking1.total_amount,
                },
                {
                    "UAICode": other_educational_institution.institutionId,
                    "status": "PENDING",
                    "confirmationLimitDate": format_into_utc_date(booking2.educationalBooking.confirmationLimitDate),
                    "totalAmount": booking2.total_amount,
                },
            ],
        }

    def test_get_all_bookings_per_year_with_no_results(self, client) -> None:
        client = client.with_eac_token()
        response = client.get("/adage/v1/years/1/prebookings")

        assert response.status_code == 200

        assert response.json == {
            "bookings": [],
        }
