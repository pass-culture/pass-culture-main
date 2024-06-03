import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date


def expected_serialized_booking(booking) -> dict:
    formats = booking.collectiveStock.collectiveOffer.formats
    formats = formats if formats else None
    return {
        "id": booking.id,
        "UAICode": booking.educationalInstitution.institutionId,
        "status": booking.status.value,
        "confirmationLimitDate": format_into_utc_date(booking.confirmationLimitDate),
        "totalAmount": booking.collectiveStock.price,
        "beginningDatetime": format_into_utc_date(booking.collectiveStock.startDatetime),
        "venueTimezone": booking.collectiveStock.collectiveOffer.venue.timezone,
        "name": booking.collectiveStock.collectiveOffer.name,
        "redactorEmail": booking.educationalRedactor.email,
        "domainIds": [domain.id for domain in booking.collectiveStock.collectiveOffer.domains],
        "domainLabels": [domain.name for domain in booking.collectiveStock.collectiveOffer.domains],
        "venueId": booking.collectiveStock.collectiveOffer.venueId,
        "venueName": booking.collectiveStock.collectiveOffer.venue.name,
        "offererName": booking.collectiveStock.collectiveOffer.venue.managingOfferer.name,
        "formats": formats,
    }


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_all_collective_bookings_per_year(self, client) -> None:
        educationalYear = EducationalYearFactory(adageId="1")
        EducationalYearFactory(adageId="2")

        educationalInstitution = EducationalInstitutionFactory()
        other_educational_institution = EducationalInstitutionFactory(institutionId="institutionId")
        EducationalYearFactory(adageId="adageId")
        booking1 = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            status="CONFIRMED",
        )
        booking2 = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=other_educational_institution,
            status="PENDING",
        )
        booking3 = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=other_educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()
        adage_id = booking1.educationalYear.adageId

        with assert_num_queries(1):
            response = client.get(f"/adage/v1/years/{adage_id}/prebookings")

        assert response.status_code == 200
        assert response.json == {
            "bookings": [
                expected_serialized_booking(booking1),
                expected_serialized_booking(booking2),
                expected_serialized_booking(booking3),
            ]
        }

    def test_get_all_collective_bookings_per_year_with_no_results(self, client) -> None:
        client = client.with_eac_token()
        response = client.get("/adage/v1/years/1/prebookings")

        assert response.status_code == 200

        assert response.json == {
            "bookings": [],
        }

    def test_get_all_collective_bookings_pagination(self, client) -> None:
        educationalYear = EducationalYearFactory()
        other_educational_year = EducationalYearFactory(adageId="adageId")
        first_bookings = CollectiveBookingFactory.create_batch(
            2,
            educationalYear=educationalYear,
        )
        CollectiveBookingFactory(educationalYear=other_educational_year)
        last_bookings = CollectiveBookingFactory.create_batch(
            8,
            educationalYear=educationalYear,
        )

        client.with_eac_token()
        base_url = f"/adage/v1/years/{educationalYear.adageId}/prebookings"

        response = client.get(f"{base_url}?per_page=2")
        assert response.status_code == 200
        assert len(response.json["bookings"]) == 2
        assert {prebooking["id"] for prebooking in response.json["bookings"]} == {
            first_bookings[0].id,
            first_bookings[1].id,
        }

        response = client.get(f"{base_url}?per_page=2&page=2")
        assert response.status_code == 200
        assert len(response.json["bookings"]) == 2
        assert {prebooking["id"] for prebooking in response.json["bookings"]} == {
            last_bookings[0].id,
            last_bookings[1].id,
        }

        response = client.get(f"{base_url}")
        assert response.status_code == 200
        assert {prebooking["id"] for prebooking in response.json["bookings"]} == {
            prebooking.id for prebooking in first_bookings + last_bookings
        }


class Returns400Test:
    def test_non_positive_page_query(self, client):
        client.with_eac_token()
        response = client.get("/adage/v1/years/fake/prebookings?page=0")
        assert response.status_code == 400

        response = client.get("/adage/v1/years/fake/prebookings?page=-1")
        assert response.status_code == 400

    def test_non_positive_per_page_query(self, client):
        client.with_eac_token()
        response = client.get("/adage/v1/years/fake/prebookings?per_page=0")
        assert response.status_code == 400

        response = client.get("/adage/v1/years/fake/prebookings?per_page=-1")
        assert response.status_code == 400
