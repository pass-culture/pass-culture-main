import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.testing import assert_num_queries
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
        educationalBooking1 = booking1.educationalBooking
        booking2 = EducationalBookingFactory(
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=other_educational_institution,
            status="PENDING",
        )
        educationalBooking2 = booking2.educationalBooking
        EducationalBookingFactory(educationalBooking__educationalYear=other_educational_year)

        client = client.with_eac_token()
        adage_id = booking1.educationalBooking.educationalYear.adageId

        with assert_num_queries(1):
            response = client.get(f"/adage/v1/years/{adage_id}/prebookings")

        assert response.status_code == 200

        assert response.json == {
            "bookings": [
                {
                    "id": educationalBooking1.id,
                    "UAICode": educationalInstitution.institutionId,
                    "status": "CONFIRMED",
                    "confirmationLimitDate": format_into_utc_date(educationalBooking1.confirmationLimitDate),
                    "totalAmount": booking1.total_amount,
                    "beginningDatetime": format_into_utc_date(booking1.stock.beginningDatetime),
                    "venueTimezone": booking1.stock.offer.venue.timezone,
                    "name": booking1.stock.offer.name,
                    "redactorEmail": educationalBooking1.educationalRedactor.email,
                },
                {
                    "id": educationalBooking2.id,
                    "UAICode": other_educational_institution.institutionId,
                    "status": "PENDING",
                    "confirmationLimitDate": format_into_utc_date(educationalBooking2.confirmationLimitDate),
                    "totalAmount": booking2.total_amount,
                    "beginningDatetime": format_into_utc_date(booking2.stock.beginningDatetime),
                    "venueTimezone": booking2.stock.offer.venue.timezone,
                    "name": booking2.stock.offer.name,
                    "redactorEmail": educationalBooking2.educationalRedactor.email,
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
