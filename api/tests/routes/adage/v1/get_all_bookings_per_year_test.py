import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def expected_serialized_booking(booking: models.CollectiveBooking) -> dict:
    formats = booking.collectiveStock.collectiveOffer.formats
    formats = [format.value for format in formats] if formats else None
    return {
        "id": booking.id,
        "UAICode": booking.educationalInstitution.institutionId,
        "status": booking.status.value,
        "additionalDetails": booking.collectiveStock.collectiveOffer.additionalDetails,
        "cancellationReason": booking.cancellationReason.value if booking.cancellationReason else None,
        "confirmationDate": format_into_utc_date(booking.confirmationDate),
        "confirmationLimitDate": format_into_utc_date(booking.confirmationLimitDate),
        "numberOfTickets": booking.collectiveStock.numberOfTickets,
        "numberOfTeachers": booking.collectiveStock.numberOfTeachers,
        "price": booking.collectiveStock.price,
        "servicePrice": booking.collectiveStock.servicePrice,
        "additionalFees": [
            {"label": fee.label or fee.type.value, "amount": fee.amount}
            for fee in booking.collectiveStock.collectiveAdditionalFees
        ],
        "startDatetime": format_into_utc_date(booking.collectiveStock.startDatetime),
        "endDatetime": format_into_utc_date(booking.collectiveStock.endDatetime),
        "venueTimezone": booking.collectiveStock.collectiveOffer.venue.offererAddress.address.timezone,
        "name": booking.collectiveStock.collectiveOffer.name,
        "redactorEmail": booking.educationalRedactor.email,
        "domainIds": [domain.id for domain in booking.collectiveStock.collectiveOffer.domains],
        "domainLabels": [domain.name for domain in booking.collectiveStock.collectiveOffer.domains],
        "venueId": booking.collectiveStock.collectiveOffer.venueId,
        "venueName": booking.collectiveStock.collectiveOffer.venue.name,
        "offererName": booking.collectiveStock.collectiveOffer.venue.managingOfferer.name,
        "formats": formats,
    }


class Returns200Test:
    def test_get_all_collective_bookings_per_year(self, client: TestClient):
        educationalYear = factories.EducationalYearFactory(adageId="1")
        factories.EducationalYearFactory(adageId="2")

        educationalInstitution = factories.EducationalInstitutionFactory()
        other_educational_institution = factories.EducationalInstitutionFactory(institutionId="institutionId")
        factories.EducationalYearFactory(adageId="adageId")
        booking1 = factories.CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        booking2 = factories.CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=other_educational_institution,
            status=models.CollectiveBookingStatus.PENDING,
        )
        booking3 = factories.CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=other_educational_institution,
            status=models.CollectiveBookingStatus.PENDING,
        )
        booking4 = factories.CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=other_educational_institution,
            status=models.CollectiveBookingStatus.CANCELLED,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
        )

        client = client.with_eac_token()
        adage_id = booking1.educationalYear.adageId

        # select bookings + selectinload additional fees
        with assert_num_queries(2):
            response = client.get(f"/adage/v1/years/{adage_id}/prebookings")

        assert response.status_code == 200
        assert response.json == {
            "bookings": [
                expected_serialized_booking(booking1),
                expected_serialized_booking(booking2),
                expected_serialized_booking(booking3),
                expected_serialized_booking(booking4),
            ]
        }

    def test_get_all_collective_bookings_per_year_with_no_results(self, client: TestClient):
        client = client.with_eac_token()
        response = client.get("/adage/v1/years/1/prebookings")

        assert response.status_code == 200

        assert response.json == {
            "bookings": [],
        }

    def test_get_all_collective_bookings_pagination(self, client: TestClient):
        educationalYear = factories.EducationalYearFactory()
        other_educational_year = factories.EducationalYearFactory(adageId="adageId")
        first_bookings = factories.CollectiveBookingFactory.create_batch(
            2,
            educationalYear=educationalYear,
        )
        factories.CollectiveBookingFactory(educationalYear=other_educational_year)
        last_bookings = factories.CollectiveBookingFactory.create_batch(
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

    def test_booking_status(self, client: TestClient):
        educational_year = factories.EducationalYearFactory()

        pending_booking = factories.PendingCollectiveBookingFactory(educationalYear=educational_year)
        confirmed_booking = factories.ConfirmedCollectiveBookingFactory(educationalYear=educational_year)
        used_booking = factories.UsedCollectiveBookingFactory(educationalYear=educational_year)
        pending_reimbursement_booking = factories.PendingReimbursementCollectiveBookingFactory(
            educationalYear=educational_year
        )
        reimbursed_booking = factories.ReimbursedCollectiveBookingFactory(educationalYear=educational_year)
        cancelled_bo_booking = factories.CancelledCollectiveBookingFactory(
            educationalYear=educational_year,
            cancellationReason=models.CollectiveBookingCancellationReasons.BACKOFFICE,
        )
        refused_institute_booking = factories.CancelledCollectiveBookingFactory(
            educationalYear=educational_year,
            cancellationReason=models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE,
        )
        refused_headmaster_booking = factories.CancelledCollectiveBookingFactory(
            educationalYear=educational_year,
            cancellationReason=models.CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER,
        )

        adage_id = educational_year.adageId
        response = client.with_eac_token().get(f"/adage/v1/years/{adage_id}/prebookings")

        assert response.status_code == 200
        assert len(response.json["bookings"]) == 8

        status_by_booking_id = {booking["id"]: booking["status"] for booking in response.json["bookings"]}
        assert status_by_booking_id == {
            pending_booking.id: "PENDING",
            confirmed_booking.id: "CONFIRMED",
            used_booking.id: "USED",
            pending_reimbursement_booking.id: "USED",
            reimbursed_booking.id: "USED",
            cancelled_bo_booking.id: "CANCELLED",
            refused_institute_booking.id: "REFUSED",
            refused_headmaster_booking.id: "REFUSED",
        }


class Returns400Test:
    def test_non_positive_page_query(self, client: TestClient):
        client.with_eac_token()
        response = client.get("/adage/v1/years/fake/prebookings?page=0")
        assert response.status_code == 400

        response = client.get("/adage/v1/years/fake/prebookings?page=-1")
        assert response.status_code == 400

    def test_non_positive_per_page_query(self, client: TestClient):
        client.with_eac_token()
        response = client.get("/adage/v1/years/fake/prebookings?per_page=0")
        assert response.status_code == 400

        response = client.get("/adage/v1/years/fake/prebookings?per_page=-1")
        assert response.status_code == 400
