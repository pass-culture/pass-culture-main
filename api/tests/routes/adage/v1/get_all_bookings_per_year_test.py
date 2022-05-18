import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_all_bookings_per_year(self, client) -> None:  # type: ignore [no-untyped-def]
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
            educationalBooking__status=EducationalBookingStatus.REFUSED,
            status="CANCELLED",
        )
        educationalBooking2 = booking2.educationalBooking
        EducationalBookingFactory(educationalBooking__educationalYear=other_educational_year)

        client = client.with_eac_token()
        adage_id = booking1.educationalBooking.educationalYear.adageId

        with assert_num_queries(2):
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
                    "status": "REFUSED",
                    "confirmationLimitDate": format_into_utc_date(educationalBooking2.confirmationLimitDate),
                    "totalAmount": booking2.total_amount,
                    "beginningDatetime": format_into_utc_date(booking2.stock.beginningDatetime),
                    "venueTimezone": booking2.stock.offer.venue.timezone,
                    "name": booking2.stock.offer.name,
                    "redactorEmail": educationalBooking2.educationalRedactor.email,
                },
            ],
        }

    def test_get_all_bookings_per_year_with_no_results(self, client) -> None:  # type: ignore [no-untyped-def]
        client = client.with_eac_token()
        response = client.get("/adage/v1/years/1/prebookings")

        assert response.status_code == 200

        assert response.json == {
            "bookings": [],
        }

    def test_get_all_bookings_pagination(self, client) -> None:  # type: ignore [no-untyped-def]
        educationalYear = EducationalYearFactory()
        other_educational_year = EducationalYearFactory(adageId="adageId")
        first_bookings = EducationalBookingFactory.create_batch(
            2,
            educationalBooking__educationalYear=educationalYear,
        )
        EducationalBookingFactory(educationalBooking__educationalYear=other_educational_year)
        last_bookings = EducationalBookingFactory.create_batch(
            8,
            educationalBooking__educationalYear=educationalYear,
        )

        client.with_eac_token()
        base_url = f"/adage/v1/years/{educationalYear.adageId}/prebookings"

        response = client.get(f"{base_url}?per_page=2")
        assert response.status_code == 200
        assert len(response.json["bookings"]) == 2
        assert {prebooking["id"] for prebooking in response.json["bookings"]} == {
            first_bookings[0].educationalBooking.id,
            first_bookings[1].educationalBooking.id,
        }

        response = client.get(f"{base_url}?per_page=2&page=2")
        assert response.status_code == 200
        assert len(response.json["bookings"]) == 2
        assert {prebooking["id"] for prebooking in response.json["bookings"]} == {
            last_bookings[0].educationalBooking.id,
            last_bookings[1].educationalBooking.id,
        }

        response = client.get(f"{base_url}")
        assert response.status_code == 200
        assert {prebooking["id"] for prebooking in response.json["bookings"]} == {
            prebooking.educationalBooking.id for prebooking in first_bookings + last_bookings
        }

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_get_all_collective_bookings_per_year(self, client) -> None:  # type: ignore [no-untyped-def]
        educationalYear = EducationalYearFactory()
        educationalInstitution = EducationalInstitutionFactory()
        other_educational_institution = EducationalInstitutionFactory(institutionId="institutionId")
        other_educational_year = EducationalYearFactory(adageId="adageId")
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
        CollectiveBookingFactory(educationalYear=other_educational_year)

        client = client.with_eac_token()
        adage_id = booking1.educationalYear.adageId

        with assert_num_queries(2):
            response = client.get(f"/adage/v1/years/{adage_id}/prebookings")

        assert response.status_code == 200

        assert response.json == {
            "bookings": [
                {
                    "id": booking1.id,
                    "UAICode": educationalInstitution.institutionId,
                    "status": "CONFIRMED",
                    "confirmationLimitDate": format_into_utc_date(booking1.confirmationLimitDate),
                    "totalAmount": booking1.collectiveStock.price,
                    "beginningDatetime": format_into_utc_date(booking1.collectiveStock.beginningDatetime),
                    "venueTimezone": booking1.collectiveStock.collectiveOffer.venue.timezone,
                    "name": booking1.collectiveStock.collectiveOffer.name,
                    "redactorEmail": booking1.educationalRedactor.email,
                },
                {
                    "id": booking2.id,
                    "UAICode": other_educational_institution.institutionId,
                    "status": "PENDING",
                    "confirmationLimitDate": format_into_utc_date(booking2.confirmationLimitDate),
                    "totalAmount": booking2.collectiveStock.price,
                    "beginningDatetime": format_into_utc_date(booking2.collectiveStock.beginningDatetime),
                    "venueTimezone": booking2.collectiveStock.collectiveOffer.venue.timezone,
                    "name": booking2.collectiveStock.collectiveOffer.name,
                    "redactorEmail": booking2.educationalRedactor.email,
                },
            ],
        }

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_get_all_collective_bookings_per_year_with_no_results(self, client) -> None:  # type: ignore [no-untyped-def]
        client = client.with_eac_token()
        response = client.get("/adage/v1/years/1/prebookings")

        assert response.status_code == 200

        assert response.json == {
            "bookings": [],
        }

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_get_all_collective_bookings_pagination(self, client) -> None:  # type: ignore [no-untyped-def]
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
    def test_non_positive_page_query(self, client):  # type: ignore [no-untyped-def]
        client.with_eac_token()
        response = client.get("/adage/v1/years/fake/prebookings?page=0")
        assert response.status_code == 400

        response = client.get("/adage/v1/years/fake/prebookings?page=-1")
        assert response.status_code == 400

    def test_non_positive_per_page_query(self, client):  # type: ignore [no-untyped-def]
        client.with_eac_token()
        response = client.get("/adage/v1/years/fake/prebookings?per_page=0")
        assert response.status_code == 400

        response = client.get("/adage/v1/years/fake/prebookings?per_page=-1")
        assert response.status_code == 400
