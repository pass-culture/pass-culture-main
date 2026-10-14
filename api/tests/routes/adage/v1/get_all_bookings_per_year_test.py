import pytest

from pcapi.core.educational.factories import CancelledCollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import ConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.factories import PendingCollectiveBookingFactory
from pcapi.core.educational.factories import PendingReimbursementCollectiveBookingFactory
from pcapi.core.educational.factories import ReimbursedCollectiveBookingFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def expected_serialized_booking(booking: CollectiveBooking) -> dict:
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
        educationalYear = EducationalYearFactory(adageId="1")
        EducationalYearFactory(adageId="2")

        educationalInstitution = EducationalInstitutionFactory()
        other_educational_institution = EducationalInstitutionFactory(institutionId="institutionId")
        EducationalYearFactory(adageId="adageId")
        booking1 = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            status=CollectiveBookingStatus.CONFIRMED,
        )
        booking2 = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=other_educational_institution,
            status=CollectiveBookingStatus.PENDING,
        )
        booking3 = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=other_educational_institution,
            status=CollectiveBookingStatus.PENDING,
        )
        booking4 = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=other_educational_institution,
            status=CollectiveBookingStatus.CANCELLED,
            cancellationReason=CollectiveBookingCancellationReasons.OFFERER,
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

    def test_booking_status(self, client: TestClient):
        educational_year = EducationalYearFactory()

        pending_booking = PendingCollectiveBookingFactory(educationalYear=educational_year)
        confirmed_booking = ConfirmedCollectiveBookingFactory(educationalYear=educational_year)
        used_booking = UsedCollectiveBookingFactory(educationalYear=educational_year)
        pending_reimbursement_booking = PendingReimbursementCollectiveBookingFactory(educationalYear=educational_year)
        reimbursed_booking = ReimbursedCollectiveBookingFactory(educationalYear=educational_year)
        cancelled_bo_booking = CancelledCollectiveBookingFactory(
            educationalYear=educational_year,
            cancellationReason=CollectiveBookingCancellationReasons.BACKOFFICE,
        )
        refused_institute_booking = CancelledCollectiveBookingFactory(
            educationalYear=educational_year,
            cancellationReason=CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE,
        )
        refused_headmaster_booking = CancelledCollectiveBookingFactory(
            educationalYear=educational_year,
            cancellationReason=CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER,
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
