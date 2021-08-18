import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.offers.utils import offer_webapp_link
from pcapi.routes.native.v1.serialization.offers import get_serialized_offer_category
from pcapi.utils.date import format_into_utc_date

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_mark_prebooking_as_used(self, app) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        booking = EducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            status=BookingStatus.CONFIRMED,
        )

        client = TestClient(app.test_client()).with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBooking.id}/mark_as_used")

        assert response.status_code == 200

        stock = booking.stock
        offer = stock.offer
        venue = offer.venue
        educational_booking = booking.educationalBooking
        assert response.json == {
            "address": venue.address,
            "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
            "cancellationDate": None,
            "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
            "category": get_serialized_offer_category(offer),
            "city": venue.city,
            "confirmationDate": None,
            "confirmationLimitDate": format_into_utc_date(educational_booking.confirmationLimitDate),
            "coordinates": {
                "latitude": float(venue.latitude),
                "longitude": float(venue.longitude),
            },
            "creationDate": format_into_utc_date(booking.dateCreated),
            "description": offer.description,
            "durationMinutes": offer.durationMinutes,
            "expirationDate": booking.expirationDate,
            "id": educational_booking.id,
            "image": None,
            "isDigital": offer.isDigital,
            "venueName": venue.name,
            "name": offer.name,
            "postalCode": venue.postalCode,
            "price": booking.amount,
            "quantity": booking.quantity,
            "redactor": {
                "email": "jean.doux@example.com",
                "redactorFirstName": "Jean",
                "redactorLastName": "Doudou",
                "redactorCivility": "M.",
            },
            "UAICode": educational_booking.educationalInstitution.institutionId,
            "yearId": int(educational_booking.educationalYearId),
            "status": "USED_BY_INSTITUTE",
            "venueTimezone": venue.timezone,
            "totalAmount": booking.total_amount,
            "url": offer_webapp_link(offer),
            "withdrawalDetails": offer.withdrawalDetails,
        }


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_mark_prebooking_as_used_when_not_confirmed_yet(self, app) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.PENDING,
        )

        client = TestClient(app.test_client()).with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBooking.id}/mark_as_used")

        assert response.status_code == 422

        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_CONFIRMED_YET"}

    def test_mark_prebooking_as_used_when_no_educational_booking_found(self, app) -> None:
        client = TestClient(app.test_client()).with_eac_token()
        response = client.post("/adage/v1/prebookings/123/mark_as_used")

        assert response.status_code == 404

        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_FOUND"}
